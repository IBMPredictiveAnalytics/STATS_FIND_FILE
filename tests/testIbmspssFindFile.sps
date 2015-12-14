data list free/x.
begin data
1 2 3
end data.

ibmspss find file filename="employee data.sav" 
folderlist="c:/temp; c:/spss19/samples/english; c:/spss18/samples/english"
filehandle=emp
/options printsearch=yes.

get file="emp/employee data.sav".

ibmspss find file filename="employee data.sav" 
folderlist="c:/temp; c:/spss19/samples/english; c:/spss18/samples/english"
filehandle=emp SEARCHSUBFOLDERS=yes
/options printsearch=yes.

ibmspss find file filename="employee data.sav" 
ENVVARIABLE="mydata;TEMP"
filehandle=emp SEARCHSUBFOLDERS=no
/options printsearch=yes.

show handles.

ibmspss find file filename="employee data.sav" 
folderlist="c:/spss18/samples/english"
ENVVARIABLE="mydata;TEMP"
filehandle=emp2 SEARCHSUBFOLDERS=no
/options printsearch=yes.

show handles.

ibmspss find file filename="employee data.sav" 
folderlist="c:/spss18/samples"
ENVVARIABLE="mydata;TEMP"
filehandle=emp3 SEARCHSUBFOLDERS=yes
/options printsearch=yes.

show handles.

ibmspss find file filename="employee data.*" 
folderlist="c:/spss18/samples/"
filehandle=emp4 SEARCHSUBFOLDERS=yes
/options printsearch=yes.

show handles.

ibmspss find file filename="employee data.*" 
folderlist="foo;c:/spss18/samples/"
filehandle=emp5.
show handles.

ibmspss find file filename="employee data.*" 
folderlist="foo;c:/spss18/samples/english"
filehandle=emp5.
show handles.

