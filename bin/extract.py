#!/usr/bin/env python3
"""
YouTube Subscription Extractor
Comprehensive tool for extracting channel information from YouTube subscription MHTML files
"""

import re
import csv
import html
import argparse
import sys
import os
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from urllib.parse import unquote
import datetime

__version__ = "1.1.0"
__author__ = "abe238"

def convert_subscriber_count_to_raw(sub_count):
    """Convert abbreviated subscriber count to raw number"""
    if not sub_count or sub_count.strip() == '':
        return ''
    
    # Remove any extra whitespace
    sub_count = sub_count.strip()
    
    # Check if it's already a plain number (no K, M suffix)
    if re.match(r'^\d+$', sub_count):
        return sub_count
    
    # Extract number and suffix
    match = re.match(r'(\d+(?:\.\d+)?)\s*([KMkm]?)', sub_count)
    if not match:
        return sub_count  # Return original if we can't parse it
    
    number_str = match.group(1)
    suffix = match.group(2).upper() if match.group(2) else ''
    
    try:
        number = float(number_str)
        
        if suffix == 'K':
            raw_count = int(number * 1000)
        elif suffix == 'M':
            raw_count = int(number * 1000000)
        else:
            raw_count = int(number)
        
        return str(raw_count)
    
    except ValueError:
        return sub_count  # Return original if conversion fails

def extract_all_profile_images_from_mhtml(content):
    """Extract all profile image URLs from MHTML Content-Location headers"""
    
    # Pattern for Content-Location image URLs
    image_patterns = [
        r'Content-Location: (https://yt3\.googleusercontent\.com/[^\s]+s176[^\s]*)',
        r'src="(https://yt3\.googleusercontent\.com/[^"]*s176[^"]*)"',
        r'"url":"(https://yt3\.googleusercontent\.com/[^"]*s176[^"]*)"'
    ]
    
    all_images = []
    for pattern in image_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        all_images.extend(matches)
    
    # Remove duplicates while preserving order
    unique_images = []
    seen = set()
    for img in all_images:
        if img not in seen:
            unique_images.append(img)
            seen.add(img)
    
    return unique_images

def clean_mhtml_encoding(text):
    """Clean MHTML encoding artifacts"""
    text = text.replace('=3D', '=')
    text = text.replace('=\n', '')
    text = text.replace('=20', ' ')
    text = text.replace('=2C', ',')
    text = text.replace('=22', '"')
    text = text.replace('=2E', '.')
    text = text.replace('=E2=80=A2', '•')
    text = text.replace('&amp;', '&')
    text = html.unescape(text)
    return text

def extract_youtube_channels_comprehensive(mhtml_file_path, quality='comprehensive', verbose=False):
    """Extract YouTube channels with comprehensive image handling"""
    
    if verbose:
        print("🔍 Reading MHTML file...")
    
    try:
        with open(mhtml_file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
    except UnicodeDecodeError:
        # Try with different encoding
        with open(mhtml_file_path, 'r', encoding='latin1', errors='ignore') as file:
            content = file.read()
    
    if verbose:
        print("🧹 Cleaning MHTML encoding...")
    content = clean_mhtml_encoding(content)
    
    if verbose:
        print("🖼️  Extracting all profile images...")
    all_available_images = extract_all_profile_images_from_mhtml(content)
    if verbose:
        print(f"   Found {len(all_available_images)} profile image URLs")
    
    channels = []
    seen_handles = set()
    used_images = set()
    
    if verbose:
        print("📊 Extracting channel data...")
    
    # Extract channel sections
    channel_pattern = r'ytd-channel-renderer[^>]*>.*?</ytd-channel-renderer>'
    channel_sections = re.findall(channel_pattern, content, re.DOTALL)
    
    if verbose:
        print(f"Found {len(channel_sections)} ytd-channel-renderer sections")
    
    for i, section in enumerate(channel_sections):
        try:
            channel_data = {
                'ChannelName': '',
                'ChannelLink': '',
                'ChannelImage': '',
                'SubscriberCount': '',
                'SubsCountRaw': '',
                'ChannelDescription': ''
            }
            
            # Extract channel URL and handle
            url_match = re.search(r'href="(https://www\.youtube\.com/@([^"]+))"', section)
            if not url_match:
                continue
                
            channel_data['ChannelLink'] = url_match.group(1)
            handle = url_match.group(2)
            
            if handle in seen_handles:
                continue
            seen_handles.add(handle)
            
            # Extract channel name
            name_patterns = [
                r'<yt-formatted-string[^>]*class="[^"]*ytd-channel-name[^"]*"[^>]*>([^<]+)</yt-formatted-string>',
                r'title="([^"]*' + re.escape(handle) + r'[^"]*)"',
                r'aria-label="([^"]*' + re.escape(handle) + r'[^"]*)"'
            ]
            
            for pattern in name_patterns:
                name_match = re.search(pattern, section, re.IGNORECASE)
                if name_match:
                    name = name_match.group(1).strip()
                    if len(name) > 1 and 'subscriber' not in name.lower():
                        channel_data['ChannelName'] = name
                        break
            
            if not channel_data['ChannelName']:
                channel_data['ChannelName'] = handle.replace('_', ' ').replace('-', ' ').title()
            
            # Extract subscriber count
            sub_patterns = [
                r'<span[^>]*id="video-count"[^>]*>([^<]*subscribers?[^<]*)</span>',
                r'(\d+(?:\.\d+)?[KM]?)\s+subscribers?',
                r'subscribers?[^0-9]*(\d+(?:\.\d+)?[KM]?)',
            ]
            
            for pattern in sub_patterns:
                sub_match = re.search(pattern, section, re.IGNORECASE)
                if sub_match:
                    sub_text = sub_match.group(1)
                    num_match = re.search(r'(\d+(?:\.\d+)?[KM]?)', sub_text)
                    if num_match:
                        channel_data['SubscriberCount'] = num_match.group(1)
                        channel_data['SubsCountRaw'] = convert_subscriber_count_to_raw(num_match.group(1))
                        break
            
            # Extract description (skip in fast mode)
            if quality == 'comprehensive':
                desc_patterns = [
                    r'<yt-formatted-string[^>]*id="description"[^>]*>([^<]+(?:\s+[^<]+)*)</yt-formatted-string>',
                    r'id="description"[^>]*>([^<]*[A-Z][^<]*\.[^<]*)</[^>]*>',
                ]
                
                for pattern in desc_patterns:
                    desc_match = re.search(pattern, section, re.IGNORECASE | re.DOTALL)
                    if desc_match:
                        desc = desc_match.group(1).strip()
                        desc = re.sub(r'\s+', ' ', desc)
                        desc = desc.replace('\n', ' ').replace('\r', ' ')
                        
                        if (len(desc) > 10 and 
                            'subscriber' not in desc.lower() and 
                            not re.match(r'^\d+[KM]?$', desc)):
                            channel_data['ChannelDescription'] = desc[:500]
                            break
            
            # Extract profile image - try multiple approaches
            img_patterns = [
                r'src="(https://yt3\.googleusercontent\.com/[^"]*s176[^"]*)"',
                r'"url":"(https://yt3\.googleusercontent\.com/[^"]*s176[^"]*)"',
            ]
            
            for pattern in img_patterns:
                img_match = re.search(pattern, section)
                if img_match:
                    img_url = img_match.group(1)
                    channel_data['ChannelImage'] = img_url
                    used_images.add(img_url)
                    break
            
            channels.append(channel_data)
            
            # Show progress for first few channels
            if verbose and len(channels) <= 10 and (channel_data['SubscriberCount'] or channel_data['ChannelDescription']):
                print(f"✅ Found: {channel_data['ChannelName']} - {channel_data['SubscriberCount']} - Image: {'Yes' if channel_data['ChannelImage'] else 'No'}")
                
        except Exception as e:
            if verbose:
                print(f"⚠️ Error processing section {i}: {e}")
            continue
    
    # Assign remaining images to channels without images (comprehensive mode only)
    if quality == 'comprehensive':
        if verbose:
            print(f"\n🔗 Assigning remaining images to channels without images...")
        unused_images = [img for img in all_available_images if img not in used_images]
        
        channels_without_images = [ch for ch in channels if not ch['ChannelImage']]
        assigned_count = 0
        
        for i, channel in enumerate(channels_without_images):
            if assigned_count < len(unused_images):
                channel['ChannelImage'] = unused_images[assigned_count]
                assigned_count += 1
                
                if verbose and assigned_count <= 10:
                    print(f"   📷 Assigned image to: {channel['ChannelName']}")
    
    # Remove duplicates and sort
    unique_channels = []
    seen_urls = set()
    
    for channel in channels:
        if channel['ChannelLink'] not in seen_urls:
            seen_urls.add(channel['ChannelLink'])
            unique_channels.append(channel)
    
    unique_channels.sort(key=lambda x: x['ChannelName'].lower())
    
    return unique_channels

def save_channels_to_csv(channels, output_file, verbose=False):
    """Save channels to CSV file"""
    if not channels:
        print("❌ No channels found to save.")
        return False
    
    fieldnames = ['ChannelName', 'ChannelLink', 'ChannelImage', 'SubscriberCount', 'SubsCountRaw', 'ChannelDescription']
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(channels)
        
        if verbose:
            print(f"💾 Saved {len(channels)} channels to {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving CSV file: {e}")
        return False

def save_channels_to_json(channels, output_file, verbose=False):
    """Save channels to JSON file"""
    if not channels:
        print("❌ No channels found to save.")
        return False
    
    try:
        # Create metadata for the export
        export_data = {
            "metadata": {
                "export_date": datetime.datetime.now().isoformat(),
                "extractor_version": __version__,
                "total_channels": len(channels),
                "channels_with_subscribers": sum(1 for ch in channels if ch['SubscriberCount']),
                "channels_with_images": sum(1 for ch in channels if ch['ChannelImage']),
                "channels_with_descriptions": sum(1 for ch in channels if ch['ChannelDescription'])
            },
            "channels": channels
        }
        
        with open(output_file, 'w', encoding='utf-8') as jsonfile:
            json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
        
        if verbose:
            print(f"💾 Saved {len(channels)} channels to {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving JSON file: {e}")
        return False

def save_channels_to_xml(channels, output_file, verbose=False):
    """Save channels to XML file"""
    if not channels:
        print("❌ No channels found to save.")
        return False
    
    try:
        # Create root element
        root = ET.Element("youtube_channels")
        
        # Add metadata
        metadata = ET.SubElement(root, "metadata")
        ET.SubElement(metadata, "export_date").text = datetime.datetime.now().isoformat()
        ET.SubElement(metadata, "extractor_version").text = __version__
        ET.SubElement(metadata, "total_channels").text = str(len(channels))
        ET.SubElement(metadata, "channels_with_subscribers").text = str(sum(1 for ch in channels if ch['SubscriberCount']))
        ET.SubElement(metadata, "channels_with_images").text = str(sum(1 for ch in channels if ch['ChannelImage']))
        ET.SubElement(metadata, "channels_with_descriptions").text = str(sum(1 for ch in channels if ch['ChannelDescription']))
        
        # Add channels
        channels_element = ET.SubElement(root, "channels")
        
        for channel in channels:
            channel_elem = ET.SubElement(channels_element, "channel")
            
            # Add each field as a child element
            for field_name, field_value in channel.items():
                field_elem = ET.SubElement(channel_elem, field_name.lower())
                field_elem.text = str(field_value) if field_value else ""
        
        # Pretty print the XML
        xml_str = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent="  ")
        
        # Remove empty lines
        pretty_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])
        
        with open(output_file, 'w', encoding='utf-8') as xmlfile:
            xmlfile.write(pretty_xml)
        
        if verbose:
            print(f"💾 Saved {len(channels)} channels to {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving XML file: {e}")
        return False

def save_channels_to_sql(channels, output_file, verbose=False):
    """Save channels to SQL file"""
    if not channels:
        print("❌ No channels found to save.")
        return False
    
    try:
        with open(output_file, 'w', encoding='utf-8') as sqlfile:
            # Write SQL header
            sqlfile.write("-- YouTube Channels Export\n")
            sqlfile.write(f"-- Generated on: {datetime.datetime.now().isoformat()}\n")
            sqlfile.write(f"-- Extractor version: {__version__}\n")
            sqlfile.write(f"-- Total channels: {len(channels)}\n\n")
            
            # Create table
            sqlfile.write("-- Create table for YouTube channels\n")
            sqlfile.write("CREATE TABLE IF NOT EXISTS youtube_channels (\n")
            sqlfile.write("    id INTEGER PRIMARY KEY AUTOINCREMENT,\n")
            sqlfile.write("    channel_name VARCHAR(255) NOT NULL,\n")
            sqlfile.write("    channel_link VARCHAR(500) NOT NULL UNIQUE,\n")
            sqlfile.write("    channel_image VARCHAR(500),\n")
            sqlfile.write("    subscriber_count VARCHAR(20),\n")
            sqlfile.write("    subscriber_count_raw INTEGER,\n")
            sqlfile.write("    channel_description TEXT,\n")
            sqlfile.write("    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n")
            sqlfile.write(");\n\n")
            
            # Clear existing data
            sqlfile.write("-- Clear existing data\n")
            sqlfile.write("DELETE FROM youtube_channels;\n\n")
            
            # Insert data
            sqlfile.write("-- Insert channel data\n")
            
            for channel in channels:
                # Escape single quotes in strings
                name = channel['ChannelName'].replace("'", "''")
                link = channel['ChannelLink'].replace("'", "''")
                image = channel['ChannelImage'].replace("'", "''") if channel['ChannelImage'] else ''
                sub_count = channel['SubscriberCount'].replace("'", "''") if channel['SubscriberCount'] else ''
                sub_raw = channel['SubsCountRaw'] if channel['SubsCountRaw'] and channel['SubsCountRaw'].isdigit() else 'NULL'
                description = channel['ChannelDescription'].replace("'", "''") if channel['ChannelDescription'] else ''
                
                sqlfile.write(f"INSERT INTO youtube_channels (channel_name, channel_link, channel_image, subscriber_count, subscriber_count_raw, channel_description) VALUES\n")
                sqlfile.write(f"  ('{name}', '{link}', '{image}', '{sub_count}', {sub_raw}, '{description}');\n")
            
            sqlfile.write("\n-- Create indexes for better performance\n")
            sqlfile.write("CREATE INDEX IF NOT EXISTS idx_channel_name ON youtube_channels(channel_name);\n")
            sqlfile.write("CREATE INDEX IF NOT EXISTS idx_subscriber_count_raw ON youtube_channels(subscriber_count_raw);\n")
            sqlfile.write("\n-- End of export\n")
        
        if verbose:
            print(f"💾 Saved {len(channels)} channels to {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving SQL file: {e}")
        return False

def get_output_format_from_extension(filename):
    """Determine output format from file extension"""
    ext = Path(filename).suffix.lower()
    format_map = {
        '.csv': 'csv',
        '.json': 'json',
        '.xml': 'xml',
        '.sql': 'sql'
    }
    return format_map.get(ext, 'csv')  # Default to CSV

def save_channels(channels, output_file, output_format=None, verbose=False):
    """Save channels in the specified format"""
    if output_format is None:
        output_format = get_output_format_from_extension(output_file)
    
    save_functions = {
        'csv': save_channels_to_csv,
        'json': save_channels_to_json,
        'xml': save_channels_to_xml,
        'sql': save_channels_to_sql
    }
    
    if output_format not in save_functions:
        print(f"❌ Unsupported output format: {output_format}")
        print(f"Supported formats: {', '.join(save_functions.keys())}")
        return False
    
    return save_functions[output_format](channels, output_file, verbose)

def main():
    """Main function with argument parsing"""
    
    parser = argparse.ArgumentParser(
        description='Extract comprehensive channel information from YouTube subscription MHTML files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  {sys.argv[0]} subscriptions.mhtml
  {sys.argv[0]} subscriptions.mhtml --output my_channels.csv
  {sys.argv[0]} subscriptions.mhtml --output data.json --format json
  {sys.argv[0]} subscriptions.mhtml --output channels.xml
  {sys.argv[0]} subscriptions.mhtml --output database.sql --format sql
  {sys.argv[0]} subscriptions.mhtml --quality fast --verbose
  {sys.argv[0]} subscriptions.mhtml --output-dir ./exports/

For more information, visit: https://github.com/abe238/youtube-subscription-extractor
        """
    )
    
    parser.add_argument('input_file', 
                       help='Path to YouTube subscriptions MHTML file')
    
    parser.add_argument('--output', '-o',
                       default='youtube_channels.csv',
                       help='Output filename (default: youtube_channels.csv)')
    
    parser.add_argument('--output-dir',
                       help='Output directory path (default: current directory)')
    
    parser.add_argument('--format', '-f',
                       choices=['csv', 'json', 'xml', 'sql'],
                       help='Output format (auto-detected from file extension if not specified)')
    
    parser.add_argument('--quality',
                       choices=['fast', 'comprehensive'],
                       default='comprehensive',
                       help='Extraction quality mode (default: comprehensive)')
    
    parser.add_argument('--encoding',
                       default='utf-8',
                       help='Input file encoding (default: utf-8)')
    
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='Enable detailed progress output')
    
    parser.add_argument('--version',
                       action='version',
                       version=f'YouTube Subscription Extractor {__version__}')
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ Error: Input file not found: {args.input_file}")
        sys.exit(1)
    
    if not input_path.is_file():
        print(f"❌ Error: Input path is not a file: {args.input_file}")
        sys.exit(1)
    
    # Handle output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / args.output
    else:
        output_path = Path(args.output)
    
    # Display banner
    if args.verbose:
        print("🎯 YouTube Subscription Extractor")
        print("=" * 50)
        print(f"Input file: {input_path}")
        print(f"Output file: {output_path}")
        print(f"Quality mode: {args.quality}")
        print("=" * 50)
    
    try:
        # Extract channels
        channels = extract_youtube_channels_comprehensive(
            str(input_path), 
            quality=args.quality, 
            verbose=args.verbose
        )
        
        if not channels:
            print("❌ No channels found in the MHTML file.")
            print("\nTroubleshooting tips:")
            print("1. Ensure the file is a complete MHTML/Web Archive from YouTube")
            print("2. Check that your subscriptions are visible on YouTube")
            print("3. Try re-exporting the file with a different browser")
            sys.exit(1)
        
        # Determine output format
        output_format = args.format if args.format else get_output_format_from_extension(str(output_path))
        
        # Save in the specified format
        if save_channels(channels, str(output_path), output_format, args.verbose):
            # Display statistics
            channels_with_subs = sum(1 for ch in channels if ch['SubscriberCount'])
            channels_with_images = sum(1 for ch in channels if ch['ChannelImage'])
            channels_with_desc = sum(1 for ch in channels if ch['ChannelDescription'])
            
            print(f"\n🎉 Extraction completed successfully!")
            print(f"📊 Results:")
            print(f"   Total channels: {len(channels)}")
            print(f"   With subscriber counts: {channels_with_subs} ({channels_with_subs/len(channels)*100:.1f}%)")
            print(f"   With profile images: {channels_with_images} ({channels_with_images/len(channels)*100:.1f}%)")
            print(f"   With descriptions: {channels_with_desc} ({channels_with_desc/len(channels)*100:.1f}%)")
            print(f"📁 Output saved to: {output_path}")
            
            # Show sample of extracted channels
            if args.verbose and len(channels) > 0:
                print(f"\n📋 Sample channels:")
                for i, channel in enumerate(channels[:3]):
                    print(f"   {i+1}. {channel['ChannelName']} ({channel['SubscriberCount'] or 'No subs'})")
                
                if len(channels) > 3:
                    print(f"   ... and {len(channels) - 3} more")
        
        else:
            sys.exit(1)
            
    except FileNotFoundError:
        print(f"❌ Error: Could not find input file: {args.input_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()