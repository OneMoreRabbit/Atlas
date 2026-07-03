@echo off
REM Publish the Atlas library to the shared drive for agent ingestion.
REM Vaults are AUTHORED locally (next to the code); the share holds read-only copies.
REM Derived views should be fresh: run atlas_validate.py before publishing.
set SHARE=\172.16.32.41\raid\job\development
for %%V in (Atlas Atlas-AgentEco) do (
  echo Publishing %%V to %SHARE%\%%V ...
  robocopy "G:\VSProjects\%%V" "%SHARE%\%%V" /MIR /XD .git .obsidian /NFL /NDL /NJH /NJS
)
echo Done. robocopy exit codes 0-7 are success.
