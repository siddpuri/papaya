if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

l  ()   { ls -l $*; }
a  ()   { ls -a $*; }
al ()   { ls -al $*; }

PS1="tp \W"
if [ `whoami` == root ]; then PS1="$PS1# "; else PS1="$PS1: "; fi
export PATH=~/papaya/bin:$PATH
