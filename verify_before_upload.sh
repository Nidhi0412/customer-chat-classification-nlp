#!/bin/bash

# Verification Script for GitHub Upload
# Run this before pushing to GitHub to ensure no sensitive data is exposed

echo "=========================================="
echo "GitHub Upload Verification Script"
echo "=========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# Function to print colored output
print_error() {
    echo -e "${RED}❌ ERROR: $1${NC}"
    ((ERRORS++))
}

print_warning() {
    echo -e "${YELLOW}⚠️  WARNING: $1${NC}"
    ((WARNINGS++))
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

echo "1. Checking for .gitignore file..."
if [ -f ".gitignore" ]; then
    print_success ".gitignore exists"
else
    print_error ".gitignore not found! Create it before uploading."
fi
echo ""

echo "2. Checking for sensitive files..."
SENSITIVE_FILES=(
    ".env"
    "config.yaml"
    "secrets.json"
    "credentials.json"
    "*.key"
    "*.pem"
)

for pattern in "${SENSITIVE_FILES[@]}"; do
    if ls $pattern 2>/dev/null | grep -q .; then
        print_error "Found sensitive file matching: $pattern"
    fi
done

if [ $ERRORS -eq 0 ]; then
    print_success "No sensitive configuration files found"
fi
echo ""

echo "3. Checking for data files in main directory..."
DATA_FILES=(
    "*.csv"
    "*.xlsx"
    "*.json"
    "*.npy"
    "*.index"
)

for pattern in "${DATA_FILES[@]}"; do
    # Exclude example_data directory
    if find . -maxdepth 1 -name "$pattern" 2>/dev/null | grep -q .; then
        print_warning "Found data file in root: $pattern (should be in example_data/ or excluded)"
    fi
done
echo ""

echo "4. Checking for hardcoded credentials in Python files..."
PATTERNS=(
    "password.*=.*['\"][^'\"]"
    "api[_-]?key.*=.*['\"]sk-"
    "secret.*=.*['\"][^'\"]"
)

for pattern in "${PATTERNS[@]}"; do
    if grep -r "$pattern" --include="*.py" . 2>/dev/null | grep -v ".env" | grep -v "example" | grep -v "#" | grep -v "venv"; then
        print_error "Found potential hardcoded credential matching: $pattern"
    fi
done

if [ $ERRORS -eq 0 ]; then
    print_success "No hardcoded credentials found in Python files"
fi
echo ""

echo "5. Checking for real email addresses in documentation..."
if grep -r "@.*\.com" --include="*.md" . 2>/dev/null | grep -v "example.com" | grep -v "company.com" | grep -v "youremail" | grep -v "your_email" | grep -v "venv" | grep -v "grep -r"; then
    print_warning "Found real email addresses in documentation"
else
    print_success "No real email addresses in documentation"
fi
echo ""

echo "6. Checking for phone numbers..."
if grep -rE "\b\d{3}[-.]?\d{3}[-.]?\d{4}\b" --include="*.py" --include="*.md" . 2>/dev/null | grep -v "example" | grep -v "###" | grep -v "sample"; then
    print_warning "Found potential phone numbers"
else
    print_success "No phone numbers found"
fi
echo ""

echo "7. Checking for IP addresses..."
if grep -rE "\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b" --include="*.py" . 2>/dev/null | grep -v "127.0.0.1" | grep -v "localhost" | grep -v "0.0.0.0" | grep -v "example" | grep -v "#"; then
    print_warning "Found IP addresses in code"
else
    print_success "No hardcoded IP addresses found"
fi
echo ""

echo "8. Checking for large files..."
if find . -type f -size +10M 2>/dev/null | grep -v ".git" | grep -v "venv" | grep -v ".index"; then
    print_warning "Found large files (>10MB) - consider using Git LFS"
else
    print_success "No large files found"
fi
echo ""

echo "9. Verifying example data is synthetic..."
if [ -d "example_data" ]; then
    print_success "example_data directory exists"
    
    # Check if example files contain warning about synthetic data
    if grep -r "synthetic" example_data/ 2>/dev/null | grep -q .; then
        print_success "Example data is marked as synthetic"
    else
        print_warning "Example data should be clearly marked as synthetic"
    fi
else
    print_warning "example_data directory not found"
fi
echo ""

echo "10. Checking for TODO or FIXME comments with sensitive info..."
if grep -r "TODO.*password\|FIXME.*key\|TODO.*secret" --include="*.py" . 2>/dev/null | grep -v "venv"; then
    print_warning "Found TODO/FIXME comments mentioning sensitive data"
else
    print_success "No sensitive TODOs found"
fi
echo ""

echo "11. Verifying required documentation exists..."
REQUIRED_DOCS=(
    "README.md"
    "LICENSE"
    "requirements.txt"
    ".gitignore"
)

for doc in "${REQUIRED_DOCS[@]}"; do
    if [ -f "$doc" ]; then
        print_success "$doc exists"
    else
        print_error "$doc is missing"
    fi
done
echo ""

echo "12. Checking git status..."
if [ -d ".git" ]; then
    echo "Files to be committed:"
    git status --short
    echo ""
    
    echo "Checking for staged sensitive files..."
    if git diff --cached --name-only | grep -E "\.env$|\.csv$|\.xlsx$|\.json$" | grep -v "example_data" | grep -v "requirements" | grep -v "package"; then
        print_error "Sensitive files are staged for commit!"
    else
        print_success "No sensitive files staged"
    fi
else
    print_warning "Not a git repository. Run 'git init' first."
fi
echo ""

# Summary
echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo ""

if [ $ERRORS -gt 0 ]; then
    print_error "Found $ERRORS error(s) - DO NOT UPLOAD until fixed!"
    echo ""
    echo "Please fix the errors above before pushing to GitHub."
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Found $WARNINGS warning(s) - Review before uploading${NC}"
    echo ""
    echo "Review the warnings above. If they're acceptable, you can proceed."
    exit 0
else
    print_success "All checks passed! Safe to upload to GitHub."
    echo ""
    echo "Next steps:"
    echo "1. git add ."
    echo "2. git commit -m 'Initial commit: Chat Classification System'"
    echo "3. git remote add origin <your-repo-url>"
    echo "4. git push -u origin main"
    exit 0
fi
