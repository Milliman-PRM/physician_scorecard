rem ### CODE OWNERS: Michael Reisz, Kelsie Stevenson
rem
rem ### OBJECTIVE:
rem   	Compile User Documentation into various formats for consumption.
rem
rem ### DEVELOPER NOTES:
rem   	* PanDoc+MikTex is installed and usable.
rem     * Stand-alone images need to have a "\ " after their link to tell PanDoc not to caption them.
rem     * To get a header above a Table-Of-Contents, it needs compiled first and then slipped above the body.

SETLOCAL ENABLEDELAYEDEXPANSION

rem ### LIBRARIES, LOCATIONS, LITERALS, ETC. GO ABOVE HERE

rem Compile User guides
for /R %%f in (*_UserGuide.md) Do (
		echo Compiling documentation for %%~nf
		
		echo Compiling HTML version
		pandoc -o "%%~nf_Header.html" "%%~nf_Header.md"
		pandoc --self-contained -B "%%~nf_Header.html" --toc -o "%%~nf.html" "%%f"
		DEL "%%~nf_Header.html"

		echo Compiling PDF version
		pandoc -o "%%~nf_Header.tex" "%%~nf_Header.md"
		pandoc -s -V geometry:margin=1in --latex-engine=xelatex -B "%%~nf_Header.tex" --toc -o "%%~nf.pdf" "%%f"
		DEL "%%~nf_Header.tex"

		echo Compiling Word version
		pandoc -o "%%~nf.docx" "%%~nf_Header.md" "%%f"
	)

echo Compiling Release Notes
pandoc --self-contained -o "Release_Notes.html" "Release_Notes.md"
