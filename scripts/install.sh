#!/bin/bash

# YouTube Subscription Extractor Installation Script
# For macOS and Linux systems

set -e

echo "🎯 YouTube Subscription Extractor Installation"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Python 3.7+ is installed
check_python() {
    echo -e "${BLUE}🔍 Checking Python installation...${NC}"
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        echo -e "${GREEN}✅ Found Python ${PYTHON_VERSION}${NC}"
        
        # Check if version is 3.7 or higher
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 7 ]; then
            echo -e "${GREEN}✅ Python version is compatible${NC}"
            return 0
        else
            echo -e "${RED}❌ Python 3.7+ required. Found ${PYTHON_VERSION}${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ Python 3 not found${NC}"
        return 1
    fi
}

# Install Python if needed (macOS with Homebrew)
install_python_macos() {
    if command -v brew &> /dev/null; then
        echo -e "${YELLOW}📦 Installing Python 3 with Homebrew...${NC}"
        brew install python3
    else
        echo -e "${RED}❌ Homebrew not found. Please install Python 3.7+ manually:${NC}"
        echo "   Visit: https://www.python.org/downloads/"
        exit 1
    fi
}

# Install Python if needed (Linux)
install_python_linux() {
    if command -v apt-get &> /dev/null; then
        echo -e "${YELLOW}📦 Installing Python 3 with apt...${NC}"
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip
    elif command -v yum &> /dev/null; then
        echo -e "${YELLOW}📦 Installing Python 3 with yum...${NC}"
        sudo yum install -y python3 python3-pip
    elif command -v dnf &> /dev/null; then
        echo -e "${YELLOW}📦 Installing Python 3 with dnf...${NC}"
        sudo dnf install -y python3 python3-pip
    else
        echo -e "${RED}❌ Package manager not found. Please install Python 3.7+ manually${NC}"
        exit 1
    fi
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    else
        echo "unknown"
    fi
}

# Main installation
main() {
    echo -e "${BLUE}📋 System Information:${NC}"
    echo "   OS: $(uname -s)"
    echo "   Architecture: $(uname -m)"
    echo "   Shell: $SHELL"
    echo ""
    
    # Check Python
    if ! check_python; then
        OS=$(detect_os)
        case $OS in
            "macos")
                install_python_macos
                ;;
            "linux")
                install_python_linux
                ;;
            *)
                echo -e "${RED}❌ Unsupported operating system${NC}"
                echo "Please install Python 3.7+ manually: https://www.python.org/downloads/"
                exit 1
                ;;
        esac
        
        # Check again after installation
        if ! check_python; then
            echo -e "${RED}❌ Python installation failed${NC}"
            exit 1
        fi
    fi
    
    # Make extract.py executable
    echo -e "${BLUE}🔧 Setting up extractor script...${NC}"
    chmod +x bin/extract.py
    
    # Test the installation
    echo -e "${BLUE}🧪 Testing installation...${NC}"
    if python3 bin/extract.py --help > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Installation test passed${NC}"
    else
        echo -e "${RED}❌ Installation test failed${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}🎉 Installation completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}📚 Quick Start:${NC}"
    echo "   python3 bin/extract.py --help"
    echo "   python3 bin/extract.py your_subscriptions.mhtml"
    echo ""
    echo -e "${BLUE}📖 For detailed documentation, see README.md${NC}"
}

# Run installation
main "$@"