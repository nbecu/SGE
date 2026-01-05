import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(320,345,windowTitle="SG Snippets")

boxes = myModel.newCellsOnGrid(10, 10, name="Box")

# Primary colors
boxes.getCell(1).setValue('color', 'red')
boxes.getCell(2).setValue('color', 'blue')
boxes.getCell(3).setValue('color', 'yellow')
# Secondary colors
boxes.getCell(4).setValue('color', 'green')
boxes.getCell(5).setValue('color', 'orange')
boxes.getCell(6).setValue('color', 'purple')
# Tertiary colors
boxes.getCell(7).setValue('color', 'cyan')
boxes.getCell(8).setValue('color', 'magenta')
boxes.getCell(9).setValue('color', 'lime')
boxes.getCell(10).setValue('color', 'pink')
boxes.getCell(11).setValue('color', 'amber')
boxes.getCell(12).setValue('color', 'teal')
# Intermediate colors
boxes.getCell(13).setValue('color', 'indigo')
boxes.getCell(14).setValue('color', 'violet')
boxes.getCell(15).setValue('color', 'brown')
boxes.getCell(16).setValue('color', 'grey')
# Neutral colors
boxes.getCell(17).setValue('color', 'black')
boxes.getCell(18).setValue('color', 'white')
boxes.getCell(19).setValue('color', 'gray')
# Thematic colors - Blues
boxes.getCell(20).setValue('color', 'lightblue')
boxes.getCell(21).setValue('color', 'steelblue')
boxes.getCell(22).setValue('color', 'lightsteelblue')
boxes.getCell(23).setValue('color', 'darkblue')
boxes.getCell(24).setValue('color', 'navy')
boxes.getCell(25).setValue('color', 'royalblue')
boxes.getCell(26).setValue('color', 'skyblue')
boxes.getCell(27).setValue('color', 'powderblue')
# Thematic colors - Reds
boxes.getCell(28).setValue('color', 'tomato')
boxes.getCell(29).setValue('color', 'crimson')
boxes.getCell(30).setValue('color', 'darkred')
boxes.getCell(31).setValue('color', 'lightcoral')
boxes.getCell(32).setValue('color', 'firebrick')
boxes.getCell(33).setValue('color', 'indianred')
boxes.getCell(34).setValue('color', 'salmon')
boxes.getCell(35).setValue('color', 'rosybrown')
# Thematic colors - Greens
boxes.getCell(36).setValue('color', 'darkgreen')
boxes.getCell(37).setValue('color', 'lightgreen')
boxes.getCell(38).setValue('color', 'forestgreen')
boxes.getCell(39).setValue('color', 'seagreen')
boxes.getCell(40).setValue('color', 'olive')
boxes.getCell(41).setValue('color', 'olivedrab')
boxes.getCell(42).setValue('color', 'springgreen')
boxes.getCell(43).setValue('color', 'palegreen')
# Thematic colors - Yellows/Oranges
boxes.getCell(44).setValue('color', 'gold')
boxes.getCell(45).setValue('color', 'darkorange')
boxes.getCell(46).setValue('color', 'lightyellow')
boxes.getCell(47).setValue('color', 'khaki')
boxes.getCell(48).setValue('color', 'orange')
boxes.getCell(49).setValue('color', 'peachpuff')
boxes.getCell(50).setValue('color', 'moccasin')
boxes.getCell(51).setValue('color', 'papayawhip')
# Thematic colors - Purples/Magentas
boxes.getCell(52).setValue('color', 'mediumvioletred')
boxes.getCell(53).setValue('color', 'darkviolet')
boxes.getCell(54).setValue('color', 'plum')
boxes.getCell(55).setValue('color', 'lavender')
boxes.getCell(56).setValue('color', 'orchid')
boxes.getCell(57).setValue('color', 'thistle')
boxes.getCell(58).setValue('color', 'mediumorchid')
boxes.getCell(59).setValue('color', 'mediumpurple')
# Thematic colors - Grays
boxes.getCell(60).setValue('color', 'darkgray')
boxes.getCell(61).setValue('color', 'lightgray')
boxes.getCell(62).setValue('color', 'silver')
boxes.getCell(63).setValue('color', 'slategray')
boxes.getCell(64).setValue('color', 'dimgray')
boxes.getCell(65).setValue('color', 'gainsboro')
boxes.getCell(66).setValue('color', 'whitesmoke')
boxes.getCell(67).setValue('color', 'darkslategray')
# Thematic colors - Browns
boxes.getCell(68).setValue('color', 'saddlebrown')
boxes.getCell(69).setValue('color', 'sienna')
boxes.getCell(70).setValue('color', 'chocolate')
boxes.getCell(71).setValue('color', 'peru')
boxes.getCell(72).setValue('color', 'burlywood')
boxes.getCell(73).setValue('color', 'tan')
boxes.getCell(74).setValue('color', 'wheat')
boxes.getCell(75).setValue('color', 'cornsilk')
# Red gradient
boxes.getCell(76).setValue('color', 'darkred')
boxes.getCell(77).setValue('color', 'maroon')
boxes.getCell(78).setValue('color', 'red')
boxes.getCell(79).setValue('color', 'orangered')
boxes.getCell(80).setValue('color', 'coral')
boxes.getCell(81).setValue('color', 'lightsalmon')
boxes.getCell(82).setValue('color', 'mistyrose')
# Blue gradient
boxes.getCell(83).setValue('color', 'midnightblue')
boxes.getCell(84).setValue('color', 'darkblue')
boxes.getCell(85).setValue('color', 'blue')
boxes.getCell(86).setValue('color', 'mediumblue')
boxes.getCell(87).setValue('color', 'cornflowerblue')
boxes.getCell(88).setValue('color', 'lightsteelblue')
boxes.getCell(89).setValue('color', 'aliceblue')
# Yellow gradient
boxes.getCell(90).setValue('color', 'darkgoldenrod')
boxes.getCell(91).setValue('color', 'goldenrod')
boxes.getCell(92).setValue('color', 'gold')
boxes.getCell(93).setValue('color', 'yellow')
boxes.getCell(94).setValue('color', 'lightyellow')
boxes.getCell(95).setValue('color', 'lemonchiffon')
boxes.getCell(96).setValue('color', 'ivory')
# Additional colors
boxes.getCell(97).setValue('color', 'turquoise')
boxes.getCell(98).setValue('color', 'hotpink')
boxes.getCell(99).setValue('color', 'limegreen')
boxes.getCell(100).setValue('color', 'darkorange')


colorDict = {}
for aColor in boxes.getEntities():
    color_value = aColor.value('color')
    if color_value is None:
        continue  # Skip entities without color
    
    color_name = str(color_value)
    if hasattr(Qt, color_name):
        colorDict[color_name] = getattr(Qt, color_name)
    else:
        print(f"Warning: Color '{color_name}' not found in Qt, using gray as default")
        colorDict[color_name] = Qt.gray
    

boxes.newPov("color", "color",colorDict)

boxes.setTooltip("color", "color")

myModel.launch()

sys.exit(monApp.exec_())
