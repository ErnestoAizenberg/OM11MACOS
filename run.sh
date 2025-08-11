#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

TAILWIND_INPUT="app/static/css/input.css"
TAILWIND_OUTPUT="app/static/dist/css/styles.css"
TAILWIND_CONFIG="tailwind.config.js"

check_dependencies() {
  if ! command -v npx &> /dev/null; then
    echo -e "${RED}Error: npx is not installed. Please install Node.js and npm.${NC}"
    exit 1
  fi
}

compile_tailwind() {
  echo -e "${GREEN}Compiling Tailwind CSS with DaisyUI...${NC}"

  if ! npx -y tailwindcss@3.3.3 \
    -i "$TAILWIND_INPUT" \
    -o "$TAILWIND_OUTPUT" \
    --config "$TAILWIND_CONFIG" \
    --minify; then
    echo -e "${RED}Error: Tailwind compilation failed${NC}"
    exit 1
  fi

  echo -e "${GREEN}Successfully compiled to ${TAILWIND_OUTPUT}${NC}"
}

main() {
  check_dependencies

  case "$1" in
    tail|tailwind)
      compile_tailwind
      ;;
    *)
      echo -e "${YELLOW}Usage: $0 {tail|tailwind}${NC}"
      exit 1
      ;;
  esac
}

main "$@"
