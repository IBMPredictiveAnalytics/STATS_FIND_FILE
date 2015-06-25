from __future__ import with_statement
#/***********************************************************************
# * Licensed Materials - Property of IBM 
# *
# * IBM SPSS Products: Statistics Common
# *
# * (C) Copyright IBM Corp. 1989, 2014
# *
# * US Government Users Restricted Rights - Use, duplication or disclosure
# * restricted by GSA ADP Schedule Contract with IBM Corp. 
# ************************************************************************/

"""STATS FIND FILE extension command"""

#Licensed Materials - Property of IBM
#IBM SPSS Products: Statistics General
#(c) Copyright IBM Corp. 2010, 2011
#US Government Users Restricted Rights - Use, duplication or disclosure restricted by GSA ADP Schedule Contract with IBM Corp.

__author__ =  'SPSS, JKP'
__version__=  '1.0.2'

helptext = """
STATS FIND FILE extension command.

STATS FIND FILE FILENAME="filename" FILEHANDLE=handlename
[FOLDERLIST="semicolon-separated list of folders"]
[ENVVARIABLE="semi-colon-separated environment variable names"]
[SEARCHSUBFOLDERS={YES|NO*}]
[/OPTIONS [PRINTSEARCH={YES|NO*}] [PRINTHANDLE={YES*|NO}]]
[/HELP]

Example:
STATS FIND FILE FILENAME="employee data.*" FILEHANDLE=employee
FOLDERLIST="c:/spss19/samples/english;c:/spss18/samples/english".

This command defines a file handle for the folder where the first instance
of the specified file or wildcard is found.

FILENAME specifies the file or file wildcard to locate.
FILEHANDLE specifies the name of the handle to be assigned.

Specify either or both of FOLDERLIST and ENVVARIABLE.  FOLDERLIST
is a string in quotes listing the folder or folders to search.  Separate
folder specifications with a semi-colon.

ENVVARIABLE is a string in quotes listing one or more environment variables
that list a folder or folders to search.  Again, specifications are separated by
a semicolon.  By using this feature, you can avoid the need to specify
specific locations for files, leaving that to your system or user environment.

If both FOLDERLIST and ENVVARIABLE are specified, the FOLDERLIST
is searched first.

By default, only the listed locations are searched.  Specify 
SEARCHSUBFOLDERS=YES to search all the subfolders of folders listed.

By default, the generated handle is displayed.  Specify PRINTHANDLE=NO
to suppress this.

Specify PRINTSEARCH=YES to display a table listing all the locations
searched in the order they were searched.

If a listed folder or environment variable does not exist, it is ignored/

If the specified file is not found, an error is raised.

/HELP displays this help and does nothing else.
"""
import spss, spssaux
from extension import Template, Syntax, processcmd
import os, fnmatch


def findfile(filename, filehandle, folderlist="", envvariable="",
    searchsubfolders=False, printsearch=False, printhandle=True):
    """Define a handle or fail based on specified search strategy
    
    Arguments are as defined in Syntax object"""
    
    if not (folderlist or envvariable):
        raise ValueError(_("Error: must specify either folderlist or envvariable or both"))
    folderlist = [f.strip() for f in folderlist.split(";")]
    envvariable = [f.strip() for f in envvariable.split(";")]
    handle = False
    
    if printsearch:
        searchpt = NonProcPivotTable("File Search", outlinetitle=_("File Search"),
            tabletitle=_("Searches for file: %s" % filename), columnlabels=[_("Folders Searched")])
    else:
        searchpt = None
        
    for searcher in [dofolderlist, doenvlist]:
        res = searcher(filename, folderlist, envvariable, searchsubfolders, searchpt)
        if res:
            makehandle(res, filehandle)
            handle = True
            if printsearch:
                searchpt.generate()
            if printhandle:
                pt = NonProcPivotTable("File Handle Definition", outlinetitle=_("File Handle"),
                    tabletitle=_("File Handle"), columnlabels=[_("Directory")])
                pt.addrow(rowlabel=filehandle, cvalues=[res])
                pt.generate()
            return
    if not handle:
        raise ValueError(_("No handle defined.  File not found: %s") % filename)
    

def dofolderlist(filename, folderlist, envvariable, searchsubfolders, searchpt):
    """Search for filename in folderlist and return location or ""
    
    filename is the file to find.  It may be a wildcard expression.
    folderlist is a possibly empty list of folders to search
    envvariable is ignored
    If searchsubfolders, subdirectories are also searched
    If searchpt is not None, each search location is added to the table"""
    
    for item in folderlist:
        try:    # ignore errors due to nonexistant folder
            for root, dirs, files in os.walk(item):
                if searchpt:
                    searchpt.addrow(cvalues=[root])
                if any((fnmatch.fnmatch(f, filename) for f in files)):
                    return root
                if not searchsubfolders:
                    break
        except:
            pass
    return ""

def doenvlist(filename, folderlist, envvariable, searchsubfolders, searchpt):
    """Search directories listed in envvariable and return location or "" """
    
    for item in envvariable:
        try:
            envlist = [v.strip() for v in os.environ[item].split(";")]
        except:
            continue
        res = dofolderlist(filename, envlist, envvariable, searchsubfolders, searchpt)
        if res:
            return res
    return ""
        
def makehandle(dir, handle):
    """Create a file handle
    
    dir is the path for the handle
    handle is the handle name"""
    
    # Note: with V18 this could be done with an api.  Submit used instead
    # to support V17
    
    dir = spssaux._smartquote(dir)
    spss.Submit("""FILE HANDLE %(handle)s /NAME=%(dir)s.""" % locals())
    
def Run(args):
    """Execute the STATS FIND FILE extension command"""

    args = args[args.keys()[0]]

    oobj = Syntax([
        Template("FILENAME", subc="",  ktype="literal", var="filename"),
        Template("FILEHANDLE", subc="", ktype="literal", var="filehandle"),
        Template("FOLDERLIST", subc="", ktype="literal", var="folderlist"),
        Template("ENVVARIABLE", subc="", ktype="literal", var="envvariable"),
        Template("SEARCHSUBFOLDERS", subc="", ktype="bool", var="searchsubfolders"),
        Template("PRINTSEARCH", subc="OPTIONS", ktype="bool", var="printsearch"),
        Template("PRINTHANDLE", subc="OPTIONS", ktype="bool", var="printhandle"),
        Template("HELP", subc="", ktype="bool")])
    
    #enable localization
    global _
    try:
        _("---")
    except:
        def _(msg):
            return msg
        
    # A HELP subcommand overrides all else
    if args.has_key("HELP"):
        #print helptext
        helper()
    else:
        #try:
            #import wingdbstub
            #if wingdbstub.debugger != None:
                #import time
                #wingdbstub.debugger.StopDebug()
                #time.sleep(2)
                #wingdbstub.debugger.StartDebug()
            #import thread
            #wingdbstub.debugger.SetDebugThreads({thread.get_ident(): 1}, default_policy=0)
            ## for V19 use
            ##    ###SpssClient._heartBeat(False)
        #except:
            #pass

        processcmd(oobj, args, findfile)

def helper():
    """open html help in default browser window
    
    The location is computed from the current module name"""
    
    import webbrowser, os.path
    
    path = os.path.splitext(__file__)[0]
    helpspec = "file://" + path + os.path.sep + \
         "markdown.html"
    
    # webbrowser.open seems not to work well
    browser = webbrowser.get()
    if not browser.open_new(helpspec):
        print("Help file not found:" + helpspec)        
try:    #override
    from extension import helper
except:
    pass        
def attributesFromDict(d):
    """build self attributes from a dictionary d."""

    # based on Python Cookbook, 2nd edition 6.18

    self = d.pop('self')
    for name, value in d.iteritems():
        setattr(self, name, value)
        
class NonProcPivotTable(object):
    """Accumulate an object that can be turned into a basic pivot table once a procedure state can be established"""
    
    def __init__(self, omssubtype, outlinetitle="", tabletitle="", caption="", rowdim="", coldim="", columnlabels=[],
                 procname="Messages"):
        """omssubtype is the OMS table subtype.
        caption is the table caption.
        tabletitle is the table title.
        columnlabels is a sequence of column labels.
        If columnlabels is empty, this is treated as a one-column table, and the rowlabels are used as the values with
        the label column hidden
        
        procname is the procedure name.  It must not be translated."""
        
        attributesFromDict(locals())
        self.rowlabels = []
        self.columnvalues = []
        self.rowcount = 0

    def addrow(self, rowlabel=None, cvalues=None):
        """Append a row labelled rowlabel to the table and set value(s) from cvalues.
        
        rowlabel is a label for the stub.
        cvalues is a sequence of values with the same number of values are there are columns in the table."""
        
        if cvalues is None:
            cvalues = []
        self.rowcount += 1
        if rowlabel is None:
            self.rowlabels.append(str(self.rowcount))
        else:
            self.rowlabels.append(rowlabel)
        self.columnvalues.extend(cvalues)
        
    def generate(self):
        """Produce the table assuming that a procedure state is now in effect if it has any rows."""
        
        privateproc = False
        if self.rowcount > 0:
            try:
                table = spss.BasePivotTable(self.tabletitle, self.omssubtype)
            except:
                spss.StartProcedure(self.procname)
                privateproc = True
                table = spss.BasePivotTable(self.tabletitle, self.omssubtype)
            if self.caption:
                table.Caption(self.caption)
            if self.columnlabels != []:
                table.SimplePivotTable(self.rowdim, self.rowlabels, self.coldim, self.columnlabels, self.columnvalues)
            else:
                table.Append(spss.Dimension.Place.row,"rowdim",hideName=True,hideLabels=True)
                table.Append(spss.Dimension.Place.column,"coldim",hideName=True,hideLabels=True)
                colcat = spss.CellText.String("Message")
                for r in self.rowlabels:
                    cellr = spss.CellText.String(r)
                    table[(cellr, colcat)] = cellr
            if privateproc:
                spss.EndProcedure()
