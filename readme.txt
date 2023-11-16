create: C:\Users\<UserName>\.wslconfig

write: [wsl2]
	kernelCommandLine = cgroup_no_v1=all

restart wsl:  wsl.exe --shutdown