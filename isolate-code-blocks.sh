#!/bin/bash

OUT=$(basename -s .md "$1")  # Get filename without .md extension
sed -n '/^```/,/^```/p' "$1" | sed '/^```/d' > "${OUT}.sh"
