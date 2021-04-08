# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=

# User specific aliases and functions
export PATH=$PATH:~/papaya/bin

l  ()   { ls -l $*; }
a  ()   { ls -a $*; }
al ()   { ls -al $*; }

PS1="tp \W"
if [ `whoami` == root ]; then PS1="$PS1# "; else PS1="$PS1: "; fi
