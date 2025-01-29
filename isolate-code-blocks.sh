OUT=basename -s .md $1
sed -n '/^```/,/^```/p' $1 | sed '/^```/d' > ${OUT}.sh