on run {input}
 	tell application "System Events"
	set theDir to POSIX path of (container of (item 1 of input))
	end tell
	set thePath to POSIX path of input
	set cmd to "cd " & quoted form of theDir & "; "
	set cmd to cmd & "python3 ~/src/misc/python/pdblatex/sophistory.py " & quoted form of thePath
	tell application "System Events" to set terminalIsRunning to exists application process "Terminal"
	tell application "Terminal"
		activate
		if terminalIsRunning is true then
			set win to do script with command cmd
		else
			set win to do script with command cmd in window 1
		end if
	end tell
end run
