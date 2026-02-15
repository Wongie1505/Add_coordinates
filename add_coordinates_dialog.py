import os
from qgis.PyQt import uic, QtWidgets
from qgis.PyQt.QtWidgets import QMessageBox, QFileDialog
from qgis.core import (
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsProject,
    QgsField,
    QgsFields,
    QgsVectorFileWriter,
    QgsCoordinateReferenceSystem
)
from qgis.PyQt.QtCore import QVariant

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), 'add_coordinates_dialog_base.ui')
)


class AddCoordinatesDialog(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self, parent=None):
        super(AddCoordinatesDialog, self).__init__(parent)
        self.setupUi(self)

        self.points = []
        self.ids = set()
        self.preview_layer_id = None

        self.btnAddCoordinate.setEnabled(False)
        self.cmbCRSType.setCurrentIndex(0)
        self.toggle_crs_inputs(0)

        self.cmbCRSType.currentIndexChanged.connect(self.toggle_crs_inputs)
        self.txtID.textChanged.connect(self.control_add_button)

        self.btnAddCoordinate.clicked.connect(self.add_coordinate)
        self.btnMap.clicked.connect(self.create_preview_layer)
        self.btnclear.clicked.connect(self.clear_all)
        self.btnBrowse.clicked.connect(self.browse_folder)
        self.btnSave.clicked.connect(self.save_export)

    # -------------------------------------------------------
    # Enable Add button when ID exists
    # -------------------------------------------------------
    def control_add_button(self):
        self.btnAddCoordinate.setEnabled(bool(self.txtID.text().strip()))

    # -------------------------------------------------------
    # Toggle CRS input groups
    # -------------------------------------------------------
    def toggle_crs_inputs(self, index):
        self.grpProjected.setEnabled(index == 0)
        self.grpGeographic.setEnabled(index != 0)

    # -------------------------------------------------------
    # Add Coordinate
    # -------------------------------------------------------
    def add_coordinate(self):
        try:
            point_id = self.txtID.text().strip()
            if not point_id:
                raise ValueError("ID required.")

            if point_id in self.ids:
                raise ValueError("ID must be unique.")

            if self.cmbCRSType.currentIndex() == 0:
                # Projected mode
                x = float(self.txtX.text().strip())
                y = float(self.txtY.text().strip())
                crs = QgsCoordinateReferenceSystem("EPSG:32376")

            else:
                # Geographic mode
                lat = float(self.txtLatDeg.text().strip())
                lon = float(self.txtLonDeg.text().strip())
                x, y = lon, lat
                crs = QgsCoordinateReferenceSystem("EPSG:4326")

            self.points.append({
                "id": point_id,
                "x": x,
                "y": y,
                "crs": crs
            })

            self.ids.add(point_id)
            self.clear_inputs()

            QMessageBox.information(self, "Added",
                                    f"Point {point_id} stored in memory.")

        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    # -------------------------------------------------------
    # Create Preview Layer
    # -------------------------------------------------------
    def create_preview_layer(self):
        if not self.points:
            QMessageBox.warning(self, "No Data", "No coordinates added.")
            return

        # Remove old preview safely
        if self.preview_layer_id:
            lyr = QgsProject.instance().mapLayer(self.preview_layer_id)
            if lyr:
                QgsProject.instance().removeMapLayer(self.preview_layer_id)

        first_crs = self.points[0]["crs"]

        layer = QgsVectorLayer(
            f"Point?crs={first_crs.authid()}",
            "Preview_Points",
            "memory"
        )

        provider = layer.dataProvider()

        fields = QgsFields()
        fields.append(QgsField("ID", QVariant.String))
        provider.addAttributes(fields)
        layer.updateFields()

        features = []
        for pt in self.points:
            feat = QgsFeature()
            feat.setGeometry(
                QgsGeometry.fromPointXY(
                    QgsPointXY(pt["x"], pt["y"])
                )
            )
            feat.setAttributes([pt["id"]])
            features.append(feat)

        provider.addFeatures(features)
        layer.updateExtents()

        QgsProject.instance().addMapLayer(layer)
        self.preview_layer_id = layer.id()

        QMessageBox.information(self, "Preview",
                                "Points displayed on map.")

    # -------------------------------------------------------
    # Save Export
    # -------------------------------------------------------
    def save_export(self):
        if not self.points:
            QMessageBox.warning(self, "No Data", "Nothing to save.")
            return

        folder = self.txtFolder.text().strip()
        file_name = self.txtFileName.text().strip()
        fmt = self.cmbFormat.currentText()

        if not folder or not file_name:
            QMessageBox.warning(self, "Missing Info",
                                "Folder and file name required.")
            return

        path = os.path.join(folder, f"{file_name}.{fmt.lower()}")

        # Create temp layer for saving
        first_crs = self.points[0]["crs"]

        layer = QgsVectorLayer(
            f"Point?crs={first_crs.authid()}",
            "Export_Layer",
            "memory"
        )

        provider = layer.dataProvider()
        fields = QgsFields()
        fields.append(QgsField("ID", QVariant.String))
        provider.addAttributes(fields)
        layer.updateFields()

        features = []
        for pt in self.points:
            feat = QgsFeature()
            feat.setGeometry(
                QgsGeometry.fromPointXY(
                    QgsPointXY(pt["x"], pt["y"])
                )
            )
            feat.setAttributes([pt["id"]])
            features.append(feat)

        provider.addFeatures(features)
        layer.updateExtents()

        if fmt == "CSV":
            QgsVectorFileWriter.writeAsVectorFormat(
                layer, path, "utf-8", layer.crs(), "CSV"
            )
        else:
            QgsVectorFileWriter.writeAsVectorFormat(
                layer, path, "utf-8", layer.crs(), "ESRI Shapefile"
            )

        # Remove preview layer safely
        if self.preview_layer_id:
            lyr = QgsProject.instance().mapLayer(self.preview_layer_id)
            if lyr:
                QgsProject.instance().removeMapLayer(self.preview_layer_id)

        self.preview_layer_id = None

        QMessageBox.information(self, "Saved",
                                f"File saved to {path}")

        self.close()

    # -------------------------------------------------------
    # Browse Folder
    # -------------------------------------------------------
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.txtFolder.setText(folder)

    # -------------------------------------------------------
    # Clear Everything
    # -------------------------------------------------------
    def clear_all(self):
        self.points.clear()
        self.ids.clear()
        self.clear_inputs()

        if self.preview_layer_id:
            lyr = QgsProject.instance().mapLayer(self.preview_layer_id)
            if lyr:
                QgsProject.instance().removeMapLayer(self.preview_layer_id)

        self.preview_layer_id = None

        QMessageBox.information(self, "Cleared",
                                "All memory cleared.")

    # -------------------------------------------------------
    # Clear Inputs Only
    # -------------------------------------------------------
    def clear_inputs(self):
        self.txtID.clear()
        self.txtX.clear()
        self.txtY.clear()
        self.txtLatDeg.clear()
        self.txtLonDeg.clear()
        self.btnAddCoordinate.setEnabled(False)
