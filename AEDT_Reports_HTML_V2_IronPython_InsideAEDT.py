# -*- coding: utf-8 -*-
"""
Created on Fri May 29 21:57:34 2026

@author: penghan
"""

# pip install pythonnet to allow python to interoperate with the .NET Common Language Runtime (CLR)
import clr
import sys
import os

sys.path.append('C:/Program Files/ANSYS Inc/v261/AnsysEM/common/IronPython/DLLs') # Necessary for finding IronPython.Wpf
sys.path.append('C:/Program Files/ANSYS Inc/v261/AnsysEM')
sys.path.append('C:/Program Files/ANSYS Inc/v261/AnsysEM/PythonFiles/DesktopPlugin')

clr.AddReference('IronPython.Wpf')
clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import FolderBrowserDialog, DialogResult

import ScriptEnv
ScriptEnv.Initialize('Ansoft.ElectronicsDesktop')

oDesktop.RestoreWindow()
# If the script is used within AEDT IronPython, comment out the following line
#oDesktop.OpenProject("C:/Workspace/AEDT_Report_Generation/2D_RZ_Magnetostatic_WindingTest_26R1.aedt")

oProject = oDesktop.GetActiveProject()
oDesign = oProject.GetActiveDesign()
# Need to add a short paragraph here. If the project has been solved, skip oDesign.Analyze("Setup1")
#oDesign.DeleteFullVariation("All", False)
#oProject.Save()
#oDesign.Analyze("Setup1")

oModule_report = oDesign.GetModule("ReportSetup")
oModule_fieldoverlay = oDesign.GetModule("FieldsReporter")

oEditor = oDesign.SetActiveEditor("3D Modeler")
oEditor.FitAll()

# Get the design note
report_note = oDesign.GetNoteText()

file_path = oProject.GetPath()
i1 = oDesign.GetDesignType()
i2 = oDesktop.GetVersion()
project_version = i1 + " " + i2 # e.g. Maxwell 2D 2026.1.0

# Get the solution type
solution_type = oDesign.GetSolutionType()

project_name = oProject.GetName()
design_name = oDesign.GetName() # No oDesign.GetDesignName()
# AddWarningMessage(design_name)

project_folder = os.path.dirname(oProject.GetPath()).replace('/', '\\')

# Check whether the design has been solved
# If the project has been solved, skip oDesign.Analyze("Setup1")
path_results = os.path.join(os.path.join(project_folder, project_name + ".aedtresults"), design_name + ".results")

if not os.listdir(path_results):
#    print (f"The results folder {path_results} is empty. Just solved the design.")
    AddWarningMessage("The results folder {path_results} is empty. Just solved the design.".format(path_results = path_results))
    oDesign.Analyze("Setup1")
    oProject.Save()
else:
#    print (f"The results folder {path_results} is not empty.")
    AddWarningMessage("The results folder {path_results} is not empty.".format(path_results = path_results))

# checking if the folder images exist or not in the project directory
if not os.path.exists(os.path.join(project_folder, "images")):
    
    # if the demo_folder directory is not present 
    # then create it.
    os.makedirs(os.path.join(project_folder, "images"))

images_folder = os.path.join(project_folder, "images")

design_image_name = []
design_image_path = []
report_image_name = []
report_image_path = []
field_image_name = []
field_image_path = []
mesh_image_name = []
mesh_image_path = []
view = "Dimetric", "Front", "Top"
fieldplot = []

meshplot = oModule_fieldoverlay.GetMeshPlotNames()
fieldplot = oModule_fieldoverlay.GetFieldPlotNames()

dialog = FolderBrowserDialog()
dialog.SelectedPath = images_folder

if dialog.ShowDialog() == DialogResult.OK:
    path = dialog.SelectedPath
    for i in view:
        oEditor.ExportModelImageToFile("{}\ModelView_{}_{}.jpg".format(path, design_name, i), 1200, 600,
                                       [
                                           "NAME:SaveImageParams",
                                           "ShowAxis:=", "False",
                                           "ShowGrid:=", "True",
                                           "SHowRuler:=", "True",
                                           "ShowRegion:=", "False",
                                           "Selections:=", "",
                                           "FieldPlotSelections:=", "",
                                           "FitToSelections:=", "",
                                           "FitToFieldPlotSelections:=", "",
                                           "Orientation:=", i
                                           ])
        AddWarningMessage("Export {}_{}.jpg to {}".format(design_name, i, path)) # comment out this line when running this script outside AEDT commandline window
        design_image_name.append("ModelView_{}_{}.jpg".format(design_name, i))
        design_image_path.append("{}\ModelView_{}_{}.jpg".format(path, design_name, i))
    
    for report in oModule_report.GetAllReportNames():
        AddWarningMessage("Export {}.jpg to {}".format(report, path)) # comment out this line when running this script outside AEDT commandline window
        oModule_report.ExportImageToFile(report, "{}\RecReport_{}.jpg".format(path, report), 1200, 600)
        report_image_name.append("RecReport_{}.jpg".format(report))
        report_image_path.append("{}\RecReport_{}.jpg".format(path, report))
        
    if any(fieldplot):
        for field in fieldplot:
            AddWarningMessage("Export {}.jpg to {}".format(field, path)) # comment out this line when running this script outside AEDT commandline window
#            oModule_fieldoverlay.ExportPlotImageToFile("{}\{}.jpg".format(path, field), "", "{}".format(field), "") # deprecated
            oModule_fieldoverlay.ExportPlotImageWithViewToFile("{}\FieldOverlay_{}.jpg".format(path, field),"", "{}".format(field), 1200, 600)
            field_image_name.append("FieldOverlay_{}.jpg".format(field))
            field_image_path.append("{}\FieldOverlay{}.jpg".format(path, field))
    if any(meshplot):
        for mesh in meshplot:
            oModule_fieldoverlay.ExportPlotImageWithViewToFile("{}\Mesh_{}.jpg".format(path, mesh),"", "{}".format(mesh), 1200, 600)
            mesh_image_name.append("Mesh_{}.jpg".format(mesh))
            mesh_image_path.append("{}\Mesh_{}.jpg".format(path, mesh))
    else:
        pass
else:
    pass

#import base64
## Read image and decode it based on Base64
#def encode_image(image_path):
#    with open(image_path, "rb") as image_file:
#        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
#    return encoded_image

# Add these two functions removesuffix and removeprefix as they does not exist in IronPython
def removesuffix(s, suffix):
    """Remove the given suffix from string s if it exists."""
    if suffix and s.endswith(suffix):
        return s[:-len(suffix)]
    return s
    
def removeprefix(s, prefix):
    """Remove the given prefix from string s if it exists."""
    if prefix and s.startswith(prefix):
        return s[len(prefix):]
    return s
    
def write_html(directory, output_file="C:\Workspace\AEDT_Report_Generation\AEDT_HTML_Report_Test2.html"):
    """
    Generate an HTML file displaying all images from the specified directory.
    """
    # Allowed image extensions
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')

    # Validate directory
    if not os.path.isdir(directory):
#        print(f"Invalid directory: {directory}")
        print "Invalid directory: {directory}".format(directory = directory)        
        return

    # Get list of image files
    image_files = [f for f in os.listdir(directory) if f.lower().endswith(image_extensions)]

    if not image_files:
#        print(f"No images found in: {directory}")
        print "No images found in: {directory}}".format(directory = directory)
        return

    # Start HTML content
    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta name = "EMPS" content = "Automatic Report Generation for Ansys Electronics Desktop">
    <title> Auto-generated AEDT report by EMPS </title>
    <style>
    body {
        font-family: Arial, sans-serif;
        margin: 20px auto; max-width: 1300px; border: 3px solid #e3e3e3;
        padding: 0; border-radius: 4px; 
        background-color: white; padding: 20px 20px 50px;
        /*background: url("bg-page1.jpg") no-repeat scroll 50% 0 #F3862A; */
        box-shadow: 0 5px 10px #a7a7a7, insert 0 4px 0 #ffffff;
        /* element shadow effect, create an external shadow (0, 1px 10px #a7a7a7) and an internal shadow (insert 0 1px 0 #fff) */
        color: rgb(205, 27, 27); 
        }
        .body_content {
            padding: 50px 50px 50px;
            background-color: rgb(255, 255, 255);
            color: rgb(113, 113, 113);
            }
        h0 {
            color: #FF8718;
            font-size: 38px;
            margin-bottom: 28px;
            border-bottom: 4px solid orange
            }
        h1 {
            color: #FF8718;
            font-size: 26px;
            margin-bottom: 18px;
            }
        h2 {
            color: #FF8718;
            margin-bottom: 10px;
            }
        h3 {
            color: rgb(0, 0, 0);
            font-size: 20px;
            margin-bottom: 18px;
            }
        h4 {
            color: #A6D3FF;
            font-size: 20px;
            margin-bottom: 18px;
            }
            pre {
            font-family: Calibri; font-size: 18px;
            color: white;
            background-color: #727272;
            padding: 20px;
            border: 1px solid #ccc; border-radius: 5px;
            white-space: pre-wrap;
            }
            #saveButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            border-radius: 5px;
            transition: background-color 0.3s, color 0.3s;
            }

            #saveButton:disabled {
            background-color: #808080;
            cursor: not-allowed;
            }
        table {
            border-collapse: collapse;
            width: 100%
            margin-left: auto; 
            margin-right: auto;`
            margin-top: 20px; 
            font-size: 20px;
            border: 3px solid #333; 
            Line-height: 26px;
            background-color: #1c1c1c;
            color: black;
            border-bottom: 4px solid #333; border-right: 4px solid #333;
            }
        caption {
            caption-side: top;
            padding: 8px;
            font-style: italic;
            text-align: center;
            }
        th, td {
            border: 2px solid #333;
            padding: 8px;
            text-align: center;
            }
        td:hover {
            background-color: #9c9c9c;
            }
        td:last-child {
            border-radius: 15px 0 15px 0;
            }
        th {
            background-color: #FF8718;
            text-align: center; width: 270px; font-size: 18px;
            color: black;
            }
        th:hover {
            background-color: #9c9c9c; text-decoration: underline;
            }
        a {
            color: #F290FF;
            }
        .color-text {
            color: white;
            }
        .header-bar:before {
            content: "";
            display: block;
            height: 30px;
            background-color: #FF8718;
            }
        .header-bar_title:before {
            content: "";
            display: block;
            height: 60px;
            background-image: url(data:image/png;base64,{headerbar_title});
            background-size: cover;
            }
        .header-bar_sec:before {
            content: "";
            display: block;
            height: 30px;
            background-color: #FB6EFF;
            }
        figure {
            padding: 4px;
            margin: auto;
            }
        figcaption {
            background-color: black;
            color: white;
            font-style: italic;
            padding: 4px;
            text-align: center;
            }
    </style>
        <script>
        // use javascript
        function scrollToElement(elementId) {
            const element = document.getElementById(elementId);
            if (element) {
                    element.scrollIntoView({
                        behavior: 'smooth'
                        });
                    }
            }
        </script>
</head>

<body>
<div class = "body_content">
    <div class = "header-bar_title" style="transform: rotate(180deg);"></div>
    <h0 class = "h0">
    <img src = "Icons/ansys_logo.jpg" alt="AEDT Auto Report" width="119" height="40">
    AEDT Report:
    <span style = "color: black;">{project_name}</span>
    </h0>

    <br><br><br><br>
    <div class = "header-bar_sec"></div><br>
    
    <table style = "width: 80%; margin-left: auto; margin-right: auto;">
        <caption> Design Information </caption>
        <tr>
            <th> Design Name: </th>
            <td><span class = "color-text">{design_name}</span></td>
        </tr>
        <tr>
            <th> AEDT Version: </th>
            <td><span class = "color-text">{project_version}</span></td>
        </tr>
        <tr>
           <th>  Solution Type: </th>
           <td><span class = "color-text">{solution_type}</span></td>
       </tr>
       <tr>
           <th> Report Generation Time: </th>
           <td><span class = "color-text">{report_datetime}</span></td>
       </tr>
       <tr>
           <th> PC Hostname: </th>
           <td><span class = "color-text">{pc_hostname}</span></td>
       </tr>
       <tr>
           <th> File Path: </th>
           <td><span class = "color-text">{file_path}</span></td>
       </tr>
       <tr>
           <th> User Name: </th>
           <td><span class = "color-text">{current_user}</span></td>
       </tr>
    </table>
    
    <h2> Model Description: </h2>
    
    <pre id = "content" contenteditable = "true">{design_note}</pre>
"""
    num_fig = 1
    # Add each image
    for image in image_files:
        image_path = os.path.join(directory, image).replace("\\", "/")  # Ensure web-friendly paths
        if image.startswith("ModelView"):
            html_content += '    <h2 id = "top"> Model Views: </h2>\n'
            html_content += '    <figure>\n'
            html_content += '    <img src="{image_path}" alt="{image}">\n'.format(image_path = image_path, image = image)
            html_content += '    <figcaption>Fig.{0} {1} </figcaption>\n'.format(num_fig, removeprefix(removesuffix(image, ".jpg"), "ModelView_"))
            html_content += '    </figure>\n'
            html_content += '    <br><br><br>\n'
            num_fig += 1
        else:
            pass

    for image in image_files:
        image_path = os.path.join(directory, image).replace("\\", "/")  # Ensure web-friendly paths
        if image.startswith("Mesh"):
            html_content += '    <h2 id = "top"> Mesh Plots: </h2>\n'
            html_content += '    <figure>\n'
            html_content += '    <img src="{image_path}" alt="{image}">\n'.format(image_path = image_path, image = image)
            html_content += '    <figcaption>Fig.{0} {1} </figcaption>\n'.format(num_fig, removeprefix(removesuffix(image, ".jpg"), "Mesh_"))
            html_content += '    </figure>\n'
            html_content += '    <br><br><br>\n'
            num_fig += 1
        else:
            pass
            
    for image in image_files:
        image_path = os.path.join(directory, image).replace("\\", "/")  # Ensure web-friendly paths           
        if image.startswith("FieldOverlay"):
            html_content += '    <h2 id = "top"> Field Overlay Plots: </h2>\n'
            html_content += '    <figure>\n'
            html_content += '    <img src="{image_path}" alt="{image}">\n'.format(image_path = image_path, image = image)
            html_content += '    <figcaption>Fig.{0} {1} </figcaption>\n'.format(num_fig, removeprefix(removesuffix(image, ".jpg"), "FieldOverlay_"))
            html_content += '    </figure>\n'
            html_content += '    <br><br><br>\n'
            num_fig += 1
        else:
            pass
            
    for image in image_files:
        image_path = os.path.join(directory, image).replace("\\", "/")  # Ensure web-friendly paths           
        if image.startswith("RecReport"):
            html_content += '    <h2 id = "top"> Rectangular Reports: </h2>\n'
            html_content += '    <figure>\n'
            html_content += '    <img src="{image_path}" alt="{image}">\n'.format(image_path = image_path, image = image)
            html_content += '    <figcaption>Fig.{0} {1} </figcaption>\n'.format(num_fig, removeprefix(removesuffix(image, ".jpg"), "RecReport_"))
            html_content += '    </figure>\n'
            html_content += '    <br><br><br>\n'
            num_fig += 1
        else:
            pass
            
    # End HTML
    html_content += """</div>
</body>
</html>"""

    current_user = os.environ.get('USERNAME')
    file_path = directory
    import socket
    pc_hostname = socket.gethostname()

    import datetime
    current_datetime = datetime.datetime.now()
    report_datetime = current_datetime.strftime('%y-%m-%d %H:%M:%S')
    

    final_html = html_content.replace("{project_name}", project_name) \
            .replace("{design_name}", design_name) \
            .replace("{project_version}", project_version) \
            .replace("{solution_type}", solution_type) \
            .replace("{report_datetime}", report_datetime) \
            .replace("{pc_hostname}", pc_hostname) \
            .replace("{file_path}", file_path) \
            .replace("{current_user}", current_user) \
            .replace("{design_note}", report_note)

    # Save HTML file
    try:
#        with open(output_file, "w", encoding="utf-8") as file: # This line is used in Cpython
        with open(output_file, "w") as file:           
            file.write(final_html)
#        print "HTML report generated: {output_file}".format(output_file = output_file) # This line is used in Cpython or AEDT Command Window
        AddWarningMessage("HTML report generated: {output_file}".format(output_file = output_file))
    except Exception as e:
#        print "Error writing HTML file: {e}".format(e = e) # This line is used in Cpython or AEDT Command Window
        AddWarningMessage("Error writing HTML file: {e}".format(e = e)) 
## Example usage
#if __name__ == "__main__":
##    folder_path = input("Enter the folder path containing images: ").strip()

folder_path = os.path.join("C:\Workspace\AEDT_Report_Generation", "images")
write_html(folder_path)

ScriptEnv.Shutdown()
       
       
       
       
       
  
               
            
            
            
        