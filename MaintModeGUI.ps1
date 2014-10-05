#Script to enable the customer to run maintenance mode.
#Author: John Monroe
#Date: 2/13/13
#Notes:

#Load Assembly's
[reflection.assembly]::LoadWithPartialName("'Microsoft.VisualBasic")
[System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
[System.Reflection.Assembly]::LoadWithPartialName("System.Drawing")

$ErrorActionPreference='Stop'

[array]$classDropDownArray  = "all","Sys_Exchange_ABS","App_IIS_ABS","Sys_MSCS_Cluster_ABS","SYS_RHEL6","SYS_SLES","APP_WEB_ABS","APP_SQL_ABS","APP_WINDOWSSERVICES","HW_HP_ABS","SYS_WINDOWS_ABS","APP_NOM"
[array]$ActionDropDownArray = "Admin_Event: add_host_to_suppress_table","Admin_Event: remove_host_from_suppress_table"

# This Function Returns the Selected Value and Closes the Form
function Add-Entry {
	
    if ($DropDown.SelectedItem -match ''){
        $class = 'all'
    } else {
        $class = $DropDown.SelectedItem.ToString()
    }
    if ($DropDown2.SelectedItem -match ''){
        $seconds = '3600'
    } else {
        $seconds = $DropDown.SelectedItem.ToString()
    }

    if ($Dropdown1.Text -match ''){
        $HostName = $env:COMPUTERNAME
        write-host "fubar"
        } else {
            $HostName = $DropDown1.Text
	    }

    $action = 'Admin_Event: add_host_to_suppress_table'
      
	Write-Host "Class: " $class
    Write-Host "Action: " $action
    Write-Host "Hostname: " $HostName
    Write-Host "Seconds: " $seconds
	
    $requester = $env:USERNAME
    Write-Host "Requester: " $requester
 
    $postParams = @"
       {"server_name":"$hostname","seconds":"$seconds","action":"$action","actionprocess":"admin.add_host","requester":"$requester","bem_class":"all","bem_class_affected":"$class"}
"@
      
      
    write-host "Post Params: " $postParams
    
    Invoke-RestMethod -ContentType 'application/json' -Uri http://maintmode.paas1.icloud.intel.com/mm_json -Method POST -Body $postParams
    #Invoke-RestMethod -ContentType 'application/json' -Uri http://fm7devmonitor02.amr.corp.intel.com:5000/mm_json -Method POST -Body $postParams
  

    $Form.Close()
    
}
function Remove-entry {
	
    if ($DropDown.SelectedItem -match ''){
        $class = 'all'
    } else {
        $class = $DropDown.SelectedItem.ToString()
    }

    if ($DropDown2.SelectedItem -match ''){
        $seconds = '3600'
    } else {
        $seconds = $DropDown.SelectedItem.ToString()
    }

   if ($Dropdown1.Text -match ''){
        $HostName = $env:COMPUTERNAME
        write-host "fubar"
        } else {
            $HostName = $DropDown1.Text
	    }

    $action = 'Admin_Event: remove_host_from_suppress_table'
	Write-Host "Action: " $action
    Write-Host "Class: " $class
    Write-Host "Hostname: " $HostName
	Write-Host "Seconds: " $seconds
    
    $requester = $env:USERNAME
    Write-Host "Requester: " $requester

     

    $postParams = @"
       {"server_name":"$hostname","seconds":"$seconds","action":"$action","actionprocess":"admin.remove_host","requester":"$requester","bem_class":"all","bem_class_affected":"$class"}       
"@
           
    write-host "Post Params: " $postParams
    
    Invoke-RestMethod -ContentType 'application/json' -Uri http://maintmode.paas1.icloud.intel.com/mm_json -Method POST -Body $postParams
    #Invoke-RestMethod -ContentType 'application/json' -Uri http://fm7devmonitor02.amr.corp.intel.com:5000/mm_json -Method POST -Body $postParams
   
    $Form.Close()
    
}
$Form = New-Object System.Windows.Forms.Form
$Form.width = 600
$Form.height = 400
$Form.Text = "Maintanance Mode AUTOMATION TOOL - BETA"

#class
$DropDown = new-object System.Windows.Forms.ComboBox
$DropDown.Location = new-object System.Drawing.Size(70,190)
$DropDown.Size = new-object System.Drawing.Size(170,25)
ForEach ($Item in $ClassDropDownArray) {
	$DropDown.Items.Add($Item)
}
$Form.Controls.Add($DropDown)
$DropDownLabel = new-object System.Windows.Forms.Label
$DropDownLabel.Location = new-object System.Drawing.Size(250,195) 
$DropDownLabel.size = new-object System.Drawing.Size(180,35) 
$DropDownLabel.Text = "Class: Default is 'all'."
$Form.Controls.Add($DropDownLabel)

#HostName
$DropDown1 = new-object System.Windows.Forms.TextBox
$DropDown1.Location = new-object System.Drawing.Size(70,80)
$DropDown1.Size = new-object System.Drawing.Size(180,30)
$Form.Controls.Add($DropDown1)
$DropDown1Label = new-object System.Windows.Forms.Label
$DropDown1Label.Location = new-object System.Drawing.Size(255,85) 
$DropDown1Label.size = new-object System.Drawing.Size(100,15) 
$DropDown1Label.Text = "Host Name."
$Form.Controls.Add($DropDown1Label)

#Seconds to suppress
$DropDown2 = new-object System.Windows.Forms.TextBox
$DropDown2.Location = new-object System.Drawing.Size(70,120)
$DropDown2.size = new-object System.Drawing.Size(180,10)
$Form.Controls.Add($DropDown2)
$DropDown2Label = new-object System.Windows.Forms.Label
$DropDown2Label.Location = new-object System.Drawing.Size(255,125) 
$DropDown2Label.size = new-object System.Drawing.Size(260,15) 
$DropDown2Label.Text = "Seconds to suppress: 1hr = 3600. Default is 3600."
$Form.Controls.Add($DropDown2Label)

#Create Button
$Button = new-object System.Windows.Forms.Button
$Button.Location = new-object System.Drawing.Size(70,270)
$Button.Size = new-object System.Drawing.Size(140,40)
$Button.Text = "Put your system(s) in MM"
$Button.Add_Click({Add-Entry})
$Form.Controls.Add($Button)

#Create Button
$Button = new-object System.Windows.Forms.Button
$Button.Location = new-object System.Drawing.Size(220,270)
$Button.Size = new-object System.Drawing.Size(140,40)
$Button.Text = "Remove your system(s) from MM"
$Button.Add_Click({Remove-Entry})
$Form.Controls.Add($Button)

#Cancel Button
$CancelButton = New-Object System.Windows.Forms.Button
$CancelButton.Location = New-Object System.Drawing.Size(70,320)
$CancelButton.Size = New-Object System.Drawing.Size(75,23)
$CancelButton.Text = "Cancel"
$CancelButton.Add_Click({$Form.close()})
$Form.Controls.Add($CancelButton)

$Form.Add_Shown({$Form.Activate()})
$Form.ShowDialog()

