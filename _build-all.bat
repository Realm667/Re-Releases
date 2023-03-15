@echo off
REM Start the program
GOTO :Main

REM # ================================================================================================
REM # Documentation
REM #     Spine of the program; this makes sure that the execution works as intended.
REM # ================================================================================================
:Main
REM Update the terminal window title
TITLE Realm667 Batch Selector by Ozymandias81
CALL :MainMenu
GOTO :TerminateProcess

REM # ================================================================================================
REM # Documentation
REM #     Displays the main menu
REM # ================================================================================================
:MainMenu
REM Thrash the terminal buffer
CLS
ECHO --------------------------------------------------------------
ECHO Welcome to Ozy's R667s Batch Selector, choose a game by typing
ECHO the relative entry and press ENTER. Choices have been setup
ECHO all under QWERTY keyboards.
ECHO --------------------------------------------------------------
ECHO.
ECHO  [1] Build All
ECHO  [2] Austerity
ECHO  [3] KDiZD
ECHO  [4] Sapphire
ECHO  [5] Stronghold
ECHO  [6] TCOTD1
ECHO  [7] TCOTD2
ECHO  [8] The Refinery
ECHO  [9] TUTNT Complete
ECHO  [0] TUTNT Episode 1
ECHO  [a] TUTNT Episode 2
ECHO  [b] TUTNT Episode 3
ECHO  [c] TUTNT Episode LE
ECHO  [d] ZDCMP1
ECHO  [e] ZDCMP2
ECHO  [f] ZPack
ECHO.
ECHO  [.] Exit
ECHO -----------------------------------------------------
REM Capture the user input
CALL :PromptUserInput
REM Inspect the input
GOTO :MainMenu_STDIN

REM # ================================================================================================
REM # Documentation
REM #     This function captures the standard input from the user.
REM # ================================================================================================
:PromptUserInput
SET /P STDIN=^>^>^>^>
GOTO :EOF

REM # ================================================================================================
REM # Documentation
REM #     Inspect the user's input and execute their desired action
REM # ================================================================================================
:MainMenu_STDIN
IF "%STDIN%" EQU "1" (
    CALL all_build.bat
    GOTO :MainMenu
)
IF "%STDIN%" EQU "2" (
    CALL austerity_build.bat
    GOTO :MainMenu
)
IF "%STDIN%" EQU "3" (
    CALL kdizd_build.bat
    GOTO :MainMenu
)
IF "%STDIN%" EQU "4" (
    CALL sapphire_build.bat
    GOTO :MainMenu
)
IF "%STDIN%" EQU "5" (
    CALL stronghold_build.bat
    GOTO :MainMenu
)
IF "%STDIN%" EQU "6" (
    CALL tcotd1_build.bat
    GOTO :MainMenu
)
IF "%STDIN%" EQU "7" (
    CALL tcotd2_build.bat
    GOTO :MainMenu
)
IF "%STDIN%" EQU "8" (
    CALL therefinery_build.bat
    GOTO :MainMenu
)
IF "%STDIN%" EQU "9" (
    CALL tutnt_build.bat
    GOTO :MainMenu
)
IF "%STDIN%" EQU "0" (
    CALL tnte1_build.bat
    GOTO :MainMenu
)
IF "%STDIN%" EQU "a" (
    CALL tnte2_build.bat
    GOTO :MainMenu
)
IF "%STDIN%" EQU "b" (
    CALL tnte3_build.bat
    GOTO :MainMenu
)
IF "%STDIN%" EQU "c" (
    CALL tntele_build.bat
    GOTO :MainMenu
)
IF "%STDIN%" EQU "d" (
    CALL zdcmp1_build.bat
    GOTO :MainMenu
)
IF "%STDIN%" EQU "e" (
    CALL zdcmp2_build.bat
    GOTO :MainMenu
)
IF "%STDIN%" EQU "f" (
    CALL zpack_build.bat
    GOTO :MainMenu
)
IF /I "%STDIN%" EQU "." (
    GOTO :EOF
)
IF /I "%STDIN%" EQU "U" (
    CALL :MainMenu_STDIN_BadInput
    GOTO :MainMenu
)

REM # ================================================================================================
REM # Documentation
REM #     This function displays a message to the user that the STDIN was illegal and not supported
REM # ================================================================================================
:MainMenu_STDIN_BadInput
ECHO.
ECHO ---------------------------- ERROR: INVALID OPTION -----------------------------
ECHO The provided input from the user is not either valid or supported.
ECHO Please select from the choices provided.
ECHO.
ECHO REMINDER:
ECHO If you get stuck with selector, simply close the window or press CTRL+LSHIFT+C
ECHO ---------------------------- ERROR: INVALID OPTION -----------------------------
ECHO.
PAUSE
GOTO :MainMenu

REM # ================================================================================================
REM # Documentation
REM #     Terminate the program without destroying the console process if invoked via CUI.
REM # ================================================================================================
:TerminateProcess
ECHO Closing program. . .
REM Restore the terminal window's title to something generic
TITLE Command Prompt
EXIT /B 0