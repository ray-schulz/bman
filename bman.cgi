#!/bin/bash

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

# This is so we know how long things take
time_start=$(date +%s.%N)

# Important for globbing later on
shopt -s extglob
shopt -s nullglob

# cgi.sh is required https://github.com/ray-schulz/cgi.sh
. cgi.sh

# Set whatever directories contain man pages
# SEPARATE DIRECTORIES WITH SPACES
# If a directory has stupid characters in it, like a space, escape it
manpath="/usr/share/man /usr/local/man"

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


# Go through all $manpath/$section directories to see if they exist
# Only sections with existing directories will be shown
declare -A localsections
function local_sections() {
	for d in $manpath ; do
		for s in "${!sections[@]}" ; do
			if [ -d "$d/man$s" ] ; then
				localsections[$s]="${sections[$s]}"
			fi
		done
	done
}

# Print the header
function print_header() {
	cat << "EOF"
Content-type:  text/html

<!doctype html>
<html>
<head>
EOF
	
	echo "<title>$1</title>"
	cat << "EOF"
<style>
body { font-family: monospace; }
table { width: 100%; }
td { vertical-align: middle; }
a { text-decoration: none; }
a:hover { text-decoration: underline; }
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
	
	echo "</td><td align=\"center\" width=\"40%\"><h2 style=\"margin: 0;padding:0\">$1</h2></td>"
	
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
}

# Print the footer
function print_footer() {
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
}

# List the available sections
function list_sections() {
	print_header "Manual Sections"
	
	for s in "${!localsections[@]}" ; do
		echo "<p><a href=\"?s=$s\">$s: ${localsections[$s]}</a></p>"
	done
	
	print_footer
}


function show_section() {
	section="${_QUERY[s]}"
	
	if [ -n "${localsections[$section]}" ] ; then
		print_header "Manual Section $section"
		
		echo "<table>"
		
		# TODO: Sort this crap
		i=1
		for mdir in $manpath ; do
			for page in $mdir/man$section/*.$section?(*|)@(|.gz|.bz2|.xz) ; do
				if [ $i -eq 1 ] ; then
					echo "<tr>"
				fi
				page=${page##*/}
				# TODO: Generate url encoded links
				echo "<td width=\"25%\"><a href=\"?p=$page\">${page%.$section*}</a><td>"
				
				if [ $i -eq 4 ] ; then
					echo "</tr>"
					i=0
				fi
				let i=$i+1
			done
		done
		
		echo "</table>"
		
		print_footer
	else
		list_sections
	fi
}

# Search for a page
function search() {
	declare title
	
	if [ -n "${_QUERY[s]}" ] ; then
		section=${_QUERY[s]}
		title="Manual search for ${_QUERY[q]} in section ${_QUERY[s]}"
	else
		section="?"
		title="Manual search for ${_QUERY[q]}"
	fi
	
	print_header "$title"
	
	i=1
	echo "<table>"
	for mdir in $manpath ; do
	#*.$section?(*|)@(|.gz|.bz2|.xz)
		for page in $mdir/man$section/*${_QUERY[q]}*.$section?(*|)@(|.gz|.bz2|.xz) ; do
			if [ $i -eq 1 ] ; then
				echo "<tr>"
			fi
			page=${page##*/}
			ext=${page##*.}
			temp=${page#*.}
			section=${temp%.*}
			temp=${page%.*}
			name=${temp%.*}
			
			echo "<td width=\"25%\"><a href=\"?p=$page\">$name($section)</a></td>"
			if [ $i -eq 4 ] ; then
				echo "</tr>"
				i=0
			fi
			let i=$i+1
			
		done
	done
	if [ $i -eq 2 ] || [ $i -eq 3 ] || [ $i -eq 4 ] ; then
		echo "</tr>"
	fi
	echo "</table>"
		
	print_footer
}

# Show a page
function show_page() {
	# Funny looking stuff to parse $_QUERY[p]
	page=${_QUERY[p]}
	ext=${page##*.}
	temp=${page#*.}
	section=${temp%.*}
	temp=${page%.*}
	name=${temp%.*}
	
	print_header "$name($section)"
	
	found=0
	for mdir in $manpath ; do
		if [ $found -eq 0 ] ; then
			if [ -f "$mdir/man${section:0:1}/$page" ] ; then
				found=1
				
				page="$mdir/man${section:0:1}/$page"
				ext=${page##*.}
				temp=${page#*.}
				section={$temp%.*}
				
				declare cat
				case "$ext" in
					 gz) cat=zcat ;;
					bz2) cat=bzcat ;;
					 xz) cat=xzcat ;;
					  *) cat=cat ;;
				esac
				
				mark=0
				div=0
				$cat $page | groff -T html -mandoc | while read line ; do
					if [ $mark -eq 0 ] && [ "${line%%>*}" = "<h1 align=\"center\"" ] ; then
						echo "<div style=\"float: right;text-align: right;width: 11%\">"
						mark=1
					elif [ $mark -eq 1 ] && [ "$line" = "<hr>" ] ; then
						echo "</div>"
						echo "<div style=\"margin-right: 11%\">"
						mark=2
						div=1
					elif [ $mark -eq 2 ] && [ "$line" = "<hr>" ] ; then
						mark=3
					elif [ $mark -eq 1 ] || [ $mark -eq 2 ] ; then
						if [ "$line" = "</h2>" ] ; then
							line="<small><a href=\"#top\">top</a></small></h2>"
						fi
						echo "$line"
					fi
				done
				echo "</div>"
			fi
		fi
	done
	
	if [ $found -eq 0 ] ; then
		echo "<p>$page not found</p>"
	fi
	
	print_footer	
}

# Find the local sections
local_sections

# Parse QUERY_STRING and figure out what to do
parse_query

# url decode
_QUERY[p]=$(url_decode "${_QUERY[p]}")
_QUERY[q]=$(url_decode "${_QUERY[q]}")
_QUERY[s]=$(url_decode "${_QUERY[s]}")

declare action
if [ -n "${_QUERY[p]}" ] ; then
	show_page
elif [ -n "${_QUERY[q]}" ] ; then
	search
elif [ -n "${_QUERY[s]}" ] ; then
	show_section
else
	list_sections
fi









