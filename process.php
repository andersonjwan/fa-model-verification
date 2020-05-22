<?php
    if($_SERVER['REQUEST_METHOD'] == 'POST') {
        // only run when the POST method is called

        if(isset($_FILES['fileToUpload'])) {
            // ensure the file has gone through
            $errors = [];
            $path = 'uploads/';
            $extension = 'jff';
            
            $fileName = $_FILES['fileToUpload']['name'];
            $fileTmp  = $_FILES['fileToUpload']['tmp_name'];
            $fileType = $_FILES['fileToUpload']['type'];
            $fileSize = $_FILES['fileToUpload']['size'];
            $fileExploded = explode('.', $fileName);
            $fileExt  = strtolower(end($fileExploded));
            
            $file = $path . $fileName;
            
            // error checking
            if(strcmp($fileExt, $extension) != 0) {
                // incorrect file type
                $errors[] = 'Incorrect file type: ' . $fileName . ' ' . $fileType;
            }
            
            if($fileSize > 2097152) {
                // file size to large
                $errors[] = 'File size exceeds upload limit: ' . $fileName . ' ' . $fileType;
            }
            
            // if no errors, process file
            if(empty($errors)) {
                $selectedSolution = $_POST['solutionSelection'];
                $selectedSolution = './solutions/' . $selectedSolution;
                
                // test uploaded file
                $output = shell_exec('python3.7 ./scripts/compareFA.py ' . $selectedSolution . ' ' . $fileTmp);
                //echo $output;
                
                list($finalResult, $spcString, $sysString) = explode(";", $output);                
                
                // pass results of model check
                $result = ['message' => $finalResult, 'spcString' => $spcString, 'sysString' => $sysString];
                echo json_encode($result);
            } else {
                $result = ['message' => 'NOT UPLOADED'];
                //echo json_encode($result);
            }
        }
    }
?>
