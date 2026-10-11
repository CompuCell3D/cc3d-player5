
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtXml import *
from PyQt5.QtWidgets import *
#from Utilities.XMLHandler import DomModel

class ModelEditor(QTreeView):
   
    def __init__(self, parent):
        QTreeView.__init__(self, parent)
        self.setFrameStyle(QFrame.NoFrame)
        self.parent = parent
        self.__setup_actions()
        
    def getParent(self):
        return self.parent

    def __setup_actions(self):
        self.expand_all_action = QAction("Expand All", self)
        self.expand_all_action.setToolTip("Expand all model parameters")
        self.expand_all_action.triggered.connect(self.expandAll)

        self.collapse_all_action = QAction("Collapse All", self)
        self.collapse_all_action.setToolTip("Collapse all model parameters")
        self.collapse_all_action.triggered.connect(self.collapseAll)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__show_context_menu)

    def __show_context_menu(self, position):
        menu = QMenu(self)
        menu.addAction(self.expand_all_action)
        menu.addAction(self.collapse_all_action)
        menu.exec_(self.viewport().mapToGlobal(position))

    def setParams(self):
        # Column widths should be set after setting the model!
        # Fixme: Before setting the column sizes, make sure that 
        # the number of columns is equal to 2!
        self.setColumnWidth(0, 180) # Since Qt 4.2  
        self.setColumnWidth(1, 40)
        self.header().setDefaultAlignment(Qt.AlignHCenter)
        # self.expandToDepth(0)

        """
        modelEditor.setColumnWidth(0, 180) # Since Qt 4.2  
        modelEditor.setColumnWidth(1, 40)
        modelEditor.header().setDefaultAlignment(Qt.AlignHCenter)
        modelEditor.expandToDepth(1)
        """
        #self.header().resizeSections(QHeaderView.ResizeToContents)
        #self.header().setStretchLastSection(True)
      
        """
      headers = QStringList()
      headers << self.trUtf8("Parameter") << self.trUtf8("Value")
      model = QStandardItemModel()
      model.setHorizontalHeaderLabels(headers)
      self.setModel(model)
      self.setColumnWidth(0, 180)
      selectionModel = QItemSelectionModel(model)
      self.setSelectionModel(selectionModel)
        """
