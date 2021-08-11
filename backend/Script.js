file = getArgument();
imp = IJ.openImage(file);
IJ.saveAs(imp, "Jpeg", file.replace('.dcm', '.jpg'))
imp.close();