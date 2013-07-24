#!/bin/bash

# This is so we know how long things take
time_start=$(date +%s.%N)

# Copyright 2013 Ray Schulz

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# https://github.com/ray-schulz/bman

# These commands must be in $PATH:
#   bc cat find sort uniq
# If not, add them to $PATH here:
#PATH=$PATH:/opt/find/bin

# Set whatever directories contain man pages
# SEPARATE DIRECTORIES WITH SPACES
# If a directory has stupid characters in it, like a space, escape it
manpath="/usr/share/man /usr/local/man"

# Number of columns to use when listing man pages
# Changing this may be silly, since column widths are currently hard set at 25%
# This may be changed in the future
numcolumns=4

# Manual sections
# If you're OS has different sections, here is where to edit that
declare -A sections
sections[0]="C library header files"
sections[1]="General commands"
sections[2]="System calls"
sections[3]="Library functions"
sections[4]="Special files and drivers"
sections[5]="File formats and conventions"
sections[6]="Games and screensavers"
sections[7]="Overview, conventions, and miscellaneous"
sections[8]="System administration commands and daemons"
sections[9]="Kernel routines"
sections[n]="Tcl/Tk keywords"
sections[x]="The X Window System"

# Also, manual subsections
# Something with this may be implemented in the future if I ever get around to it
# For now, leave it commented out, won't hurt anything but may as well not waste time on it
#declare -A subsections
#subsections[curses]="Curses library"
#subsections[form]="Form extension to the curses library"
#subsections[menu]="Menu extension to the curses library"
#subsections[ncurses]="New curses library"
#subsections[p]="POSIX specifications"
#subsections[pcap]="Packet Capture library"
#subsections[pm]="Perl modules"
#subsections[ssl]="Secure Socket library"
#subsections[x]="X Window System"

# This function breaks up $QUERY_STRING into an associative array $GET
# If QUERY_STRING is foo=bar&bohica&sn=afu then:
# GET[foo]=bar; GET[bohica]=; GET[sn]=afu
declare -A GET
function get_query() {
	i=0
	param=
	start=0
	length=
	while test -n "$i" ; do
		query=${QUERY_STRING:$i:1}
		length=$(($i - $start))
		temp=${QUERY_STRING:$start:$length}
		
		if [ -n "$query" ] ; then
			if [ $query = '=' ] ; then
				param=$temp
				start=$(($i + 1))
			elif [ $query = '&' ] ; then
				if [ -n "$param" ] ; then
					GET[$param]=$temp
				else
					GET[$temp]=
				fi
				param=
				start=$(($i + 1))
			fi
			i=$(($i + 1))
		else
			if [ -n "$param" ] ; then
				GET[$param]=$temp
			else
				GET[$temp]=
			fi
			i=
		fi
	done
}

# Search for a page
function search() {
	echo "<p>p: ${GET[p]}</p>"
	echo "<p>q: ${GET[q]}</p>"
	echo "<p>s: ${GET[s]}</p>"
}

# Show a page
function show_page() {
	echo "<p>p: ${GET[p]}</p>"
	echo "<p>q: ${GET[q]}</p>"
	echo "<p>s: ${GET[s]}</p>"
	
}

# go through all $manpath/$section directories to see if they exist
# only sections with existing directories will be shown
declare -A localsections
for d in $manpath ; do
	for s in "${!sections[@]}" ; do
		if [ -d "$d/man$s" ] ; then
			localsections[$s]="${sections[$s]}"
		fi
	done
done

# set the page title
if [ -n "$QUERY_STRING" ] ; then
	get_query
	
	# Search
	if [ -n "${GET[q]}" ] ; then
		if [ -n "${GET[s]}" ] ; then
			title="Manual Search for ${GET[q]} in Section ${GET[s]}"
		else
			title="Manual Search for ${GET[q]}"
		fi
	
	# Display a page or list matching pages
	elif [ -n "${GET[p]}" ] ; then
		if [ -n "${GET[s]}" ] ; then
			title="Display Manual Page ${GET[p]} in Section ${GET[s]}"
		else
			title="List Manual Page ${GET[p]} in All Sections"
		fi
	
	# List pages in a section
	elif [ -n "${GET[s]}" ] ; then
		if [ -n "${localsections[${GET[s]}]}" ] ; then
			title="Manual Section ${GET[s]}: ${localsections[${GET[s]}]}"
		
		# Bad query string!
		else
			QUERY_STRING=
		fi
	
	# Bad query string!
	else
		QUERY_STRING=
	fi
fi

# Main page
if [ ! -n "$QUERY_STRING" ] ; then
	title="Manual Sections"
fi

# Header
cat << "EOF"
Content-type:  text/html

<!doctype html>
<html>
<head>
EOF
echo "<title>$title</title>"
cat << "EOF"

<style>
body { font-family: monospace; }
table { width: 100%; }
td { vertical-align: middle; }
</style>

</head>
<body id="top">
<table>
<tr>
<td width="30%">
<a href=".">#</a> 
EOF

for s in "${!localsections[@]}" ; do
	echo -n "<a href=\"?s=$s\">$s</a> "
done

echo "</td><td align=\"center\" width=\"40%\"><strong>$title</strong></td>"

cat << "EOF"
<td align="right" width="30%">
<form>
<input type="text" name="q">
<select name="s">
<option></option>
EOF

for s in "${!localsections[@]}" ; do
	echo -n "<option style=\"text-align: center\">$s</option> "
done

cat << "EOF"
</select>
<input type="submit" value="Search">
</form>
</td>
</tr>
</table>
<hr>
EOF

# Now we can finally figure out what to do!
if [ -n "$QUERY_STRING" ] ; then
	if [ -n "${GET[q]}" ] ; then
		if [ -n "${GET[s]}" ] ; then
			title="Manual Search for ${GET[q]} in Section ${GET[s]}"
			search
		else
			title="Manual Search for ${GET[q]}"
			search
		fi
		
		
		
	elif [ -n "${GET[p]}" ] ; then
		if [ -n "${GET[s]}" ] ; then
			title="Display Manual Page ${GET[p]} in Section ${GET[s]}"
			show_page
		else
			title="List Manual Page ${GET[p]} in All Sections"
		fi
	
	# List the pages in a section
	elif [ -n "${GET[s]}" ] ; then
		i=1
		# Put them in a 4 column table for your viewing pleasure
		echo "<table>"
		
		# This line is stupid long
		# Use find and a crazy regex to find all the man pages, then pipe through sort and uniq
		find $manpath -regextype posix-extended \( -type f -or -type l \) -regex ".*\.${GET[s]}($||[abcdefghijklmnopqrstuvwxyz0123456789]+)($|\.(gz|bz2|xz)$)" -exec basename {} \; | sort -f | uniq \
		| while read page ; do 
			if [ $i = "1" ] ; then
				echo "<tr>"
			fi
			
			# remove extensions .gz, .bz2, and .xz
			page=${page%.gz}
			page=${page%.bz2}
			page=${page%.xz}
			
			#remove section number
			page=${page%.*}
			
			echo "<td width=\"25%\"><a href=\"?p=$page&s=${GET[s]}\">$page</a></td>"
			if [ $i = "$numcolumns" ] ; then
				echo "</tr>"
				i=0
			fi
			i=$(($i + 1))
		done
		echo "</table>"
	fi
else
	for s in "${!localsections[@]}" ; do
		echo "<p><a href=\"?s=$s\">$s: ${localsections[$s]}</a></p>"
	done
fi

cat << "EOF"

<hr>
<table>
<tr><td width="40%"><a href="https://github.com/ray-schulz/bman">bman</a> - the web manual browser</td>
<td align="center" width="20%"><a href="#top">top</a></td>
<td align="right" width="40%">Page generated in 
EOF
time_end=$(date +%s.%N)
echo "$time_end - $time_start" | bc
cat << "EOF"
seconds</td></tr>
</table>
</body>
</html>
EOF
