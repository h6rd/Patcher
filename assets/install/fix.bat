@echo off
setlocal enabledelayedexpansion
set "e1=46 46 46 92 46 46 92 46 46 92 100 111 116 97 92 103 97 109 101 105 110 102 111 95 98 114 97 110 99 104 115 112 101 99 105 102 105 99 46 103 105 126 83 72 65 49 58 57 51 56 66 65 67 51 56 55 68 68 65 67 68 55 56 55 69 52 54 53 57 53 54 52 68 66 65 70 54 52 48 53 69 57 49 51 68 56 51 59 67 82 67 58 70 49 54 51 54 66 51 52"
set "u_p=80 97 116 99 104 67 97 99 104 101 47 102 105 108 101 67 97 99 104 101 47 103 97 109 101 105 110 102 111 95 98 114 97 110 99 104 115 112 101 99 105 102 105 99 46 103 105"
set "g_p1=103 97 109 101"
set "g_p2=100 111 116 97"
set "g_p3=103 97 109 101 105 110 102 111 95 98 114 97 110 99 104 115 112 101 99 105 102 105 99 46 103 105"
set "p1=103 97 109 101"
set "p2=98 105 110"
set "p3=119 105 110 54 52"
set "fop=68 111 116 97 50 83 107 105 110 67 104 97 110 103 101 114"
set "p4=100 111 116 97 46 115 105 103 110 97 116 117 114 101 115"
echo.
set "mirrors=https://skinchanger.net https://ru.skinchanger.net https://en.dota2changer.com https://ru.dota2changer.com"
set "th=C:F1636B34"
taskkill /F /IM dota2.exe >nul 2>&1
set "f_s="
for %%n in (%e1%) do (
  cmd /c exit %%n
  set "f_s=!f_s!!=exitcodeAscii!"
)
set "sign_path="
for %%p in ("!p1!" "!p2!" "!p3!" "!p4!") do (
  set "part="
  for %%c in (%%~p) do (
    cmd /c exit %%c
    set "part=!part!!=exitcodeAscii!"
  )
  set "sign_path=!sign_path!\!part!"
)
set "sign_path=!sign_path:~1!"
set "gP="
if not exist "DotaPath.txt" (
	if not exist "%USERPROFILE%\Downloads\DotaPath.txt" (
		goto :NotFoundF
	) else (
		set /p dotaPath=<%USERPROFILE%\Downloads\DotaPath.txt
	)
) else (
	set /p dotaPath=<DotaPath.txt
)
if not defined dotaPath goto :NotFoundF
set "dotaPath=%dotaPath:\=/%"
set "search=common"
call :strpos "%dotaPath%" "%search%" pos
if not defined pos goto :NotFoundF
set /a endPos=pos + 6
set "cutPath=!dotaPath:~0,%endPos%!"
if exist "!cutPath!\dota 2 beta\!sign_path!" (
        set "gP=!cutPath!\dota 2 beta"
        goto :path_found
    )
goto :NotFoundF
:strpos
set "string=%~1"
set "substring=%~2"
set /a pos=0
:loop
if "!string:~%pos%,6!"=="%substring%" (
    endlocal & set "%~3=%pos%" & exit /b
)
set /a pos+=1
if "!string:~%pos,1!"=="" (
    endlocal & set "%~3=" & exit /b
)
goto loop
:NotFoundF
for /f "tokens=2*" %%a in ('reg query "HKCU\Software\Valve\Steam" /v "SteamPath" 2^>nul') do (
  set "steamPath=%%b"
  set "common_path=!steamPath!\steamapps\common\dota 2 beta"
  if exist "!common_path!\!sign_path!" (
    set "gP=!common_path!"
	goto :path_found
  )
)
set "SteamPath="
for /f "tokens=3*" %%a in ('reg query "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Valve\Steam" /v InstallPath 2^>nul') do (
    set "SteamPath=%%a %%b"
)
if not defined SteamPath (
    set "SteamPath=C:\Program Files (x86)\Steam"
)
set "VdfPath=!SteamPath!\steamapps\libraryfolders.vdf"
if not exist "!VdfPath!" (
    goto :NotFound
)
for /f "tokens=2 delims=	" %%a in ('findstr /i "path" "!VdfPath!"') do (
    set "LibPath=%%~a"
    set "LibPath=!LibPath:"=!"
    set "LibPath=!LibPath:\\=\!"
    if exist "!LibPath!\steamapps\common\dota 2 beta\!sign_path!" (
        set "gP=!LibPath!\steamapps\common\dota 2 beta"
        goto :path_found
    )
)
:NotFound
if not defined gP (
  for %%d in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    set "steam_path=%%d:\Program Files (x86)\Steam\steamapps\common\dota 2 beta"
    if exist "!steam_path!\!sign_path!" (
      set "gP=!steam_path!"
	  goto :path_found
    )
    set "steam_path=%%d:\Program Files\Steam\steamapps\common\dota 2 beta"
    if exist "!steam_path!\!sign_path!" (
      set "gP=!steam_path!"
	  goto :path_found
    )
    set "steam_path=%%d:\Steam\steamapps\common\dota 2 beta"
    if exist "!steam_path!\!sign_path!" (
      set "gP=!steam_path!"
	  goto :path_found
    )
    set "steam_path=%%d:\Games\Steam\steamapps\common\dota 2 beta"
    if exist "!steam_path!\!sign_path!" (
      set "gP=!steam_path!"
	  goto :path_found
    )
    set "steam_path=%%d:\SteamLibrary\steamapps\common\dota 2 beta"
    if exist "!steam_path!\!sign_path!" (
      set "gP=!steam_path!"
	  goto :path_found
    )
    set "steam_path=%%d:\Games\SteamLibrary\steamapps\common\dota 2 beta"
    if exist "!steam_path!\!sign_path!" (
      set "gP=!steam_path!"
	  goto :path_found
    )
  )
)
:path_found
set "expected_hash=938BAC387DDACD787E4659564DBAF6405E913D83"
if not defined gP (
  echo dota 2 beta - folder not found! You can add your path to dota 2 beta in file DotaPath.txt
  pause
  exit /b
) else (
	echo !gP! > DotaPath.txt
	if not exist "DotaPath.txt" (
		echo !gP! > "%USERPROFILE%\Downloads\DotaPath.txt"
	)
)
set "s_fl=!gP!\!sign_path!"
set "hash_exists=0"
if exist "!s_fl!" (
  findstr /C:"%th%" "!s_fl!" >nul && set "hash_exists=1"
)
if !hash_exists! equ 1 (
  echo [SUCCESS]
) else (
  >>"!s_fl!" (
    echo(
    echo !f_s!
  )
  echo [SUCCESS]
)
set "gi_path="
for %%p in ("!g_p1!" "!g_p2!" "!g_p3!") do (
  set "part="
  for %%c in (%%~p) do (
    cmd /c exit %%c
    set "part=!part!!=exitcodeAscii!"
  )
  set "gi_path=!gi_path!\!part!"
)
set "gi_path=!gi_path:~1!"
set "gi_file=!gP!\!gi_path!"
if exist "!gi_file!" (
  for /f "tokens=*" %%h in ('certutil -hashfile "!gi_file!" SHA1 ^| find /i /v "hash" ^| find /i /v "certutil"') do (
    set "current_hash=%%h"
    set "current_hash=!current_hash: =!"
    if /i "!current_hash!"=="%expected_hash%" (
      set "download_success=1"
      goto :skip_download
    )
  )
)
set "url_suffix="
for %%c in (%u_p%) do (
  cmd /c exit %%c
  set "url_suffix=!url_suffix!!=exitcodeAscii!"
)
set "download_success=0"
for %%m in (%mirrors%) do (
  if !download_success! equ 0 (
    curl --user-agent "Mozilla/5.0 FixPatcher FixPatcher_Windows" -k -f -o "!gi_file!" "%%m/!url_suffix!" >nul 2>&1 && set "download_success=1"
  )
)
if !download_success! equ 1 (
  echo [SUCCESS] gameinfo updated
) else (
  echo [ERROR] Failed to update gameinfo
)
:skip_download
set "fon="
for %%c in (%fop%) do (
  cmd /c exit %%c
  set "fon=!fon!!=exitcodeAscii!"
)
if not exist "!gP!\game\!fon!" (
  mkdir "!gP!\game\!fon!" >nul 2>&1
)
echo [PATCHING SUCCESS]
cmd.exe /c START "" "steam://rungameid/570" "-applaunch 570"
exit /b