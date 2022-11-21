import sys

import pandas as pd
import qdarktheme
import darkdetect
from PyQt6.QtCharts import (QBarCategoryAxis, QCandlestickSeries,
                            QCandlestickSet, QChart, QChartView, QLineSeries,
                            QValueAxis)
from PyQt6.QtCore import QRegularExpression, Qt, QSize
from PyQt6.QtGui import QColor, QFont, QIcon, QRegularExpressionValidator
from PyQt6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLabel,
                             QLineEdit, QMessageBox, QPushButton, QScrollArea,
                             QSizePolicy, QSpinBox, QStyle, QVBoxLayout,
                             QWidget)


class Window(QWidget):
    def change_stock_ticker(self, ticker: str) -> None:
        """ Changes stock ticker """
        self.stock_ticker = ticker
        
    def update_stock(self) -> None:
        """ Updates stock data shown in the chart """
        self.download_data()
        #print(self.df)
        if "Error" in str(self.df.iloc[0]): # wrong stock ticker selected
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Error!")
            msg_box.setText("Zadali jste špatný symbol akcie!")
            button = msg_box.exec()

            if button == QMessageBox.StandardButton.Ok: # set previous working stock ticker and download its data
                self.line_edit.setText(self.prev_stock_ticker)
                self.stock_ticker = self.prev_stock_ticker
                self.download_data()
                print("OK!")
        else:
            self.series.clear()
            self.axisX.clear()
            self.process_data()
            self.set_boundaries()
            self.prev_stock_ticker = self.stock_ticker
    
    def change_market_days(self, days: int) -> None:
        """ Changes number of market days shown """
        self.market_days_shown = days
        self.series.clear()
        self.axisX.clear()
        self.process_data()
        self.set_boundaries()

    stock_ticker = 'BA'
    prev_stock_ticker = stock_ticker 
    tm = []  # timestamp 
    market_days_shown = 20

    def download_data(self) -> None:
        """ Downloads data from AlphaVantage server """
        # api key 9FTHOZM5TKJCTYXL
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&datatype=csv&symbol='+self.stock_ticker+'&outputsize=compact&apikey=9FTHOZM5TKJCTYXL'
        try:
            self.df = pd.read_csv(url)
        except:
            print("Nepodařilo se stáhnout data")
        else:
            print("Downloaded")
    
    def create_series(self) -> None:
        """ Creates QCandlestickSeries """
        self.series = QCandlestickSeries()
        self.series.setDecreasingColor(QColor(255,0,0))
        self.series.setIncreasingColor(QColor(0,128,0))
    
    def create_rest(self) -> None:
        """ Creates the rest of objects needed """
        self.chart = QChart()
        self.chart.addSeries(self.series)  # candles
        #self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.chart.legend().hide()
        self.chart.setTheme(QChart.ChartTheme.ChartThemeQt)

        self.axisX = QBarCategoryAxis()
        self.axisX.setLabelsAngle(-90)
        self.axisX.append(self.tm)

        self.axisX.show()
        self.chart.addAxis(self.axisX, Qt.AlignmentFlag.AlignBottom)
        self.series.attachAxis(self.axisX)

        self.axisY = QValueAxis()   # axis Y
        self.axisY.show()
        self.chart.addAxis(self.axisY, Qt.AlignmentFlag.AlignLeft)
        self.series.attachAxis(self.axisY)

        self.axisY.setMax(self.y_max)
        self.axisY.setMin(self.y_min)
        

        self.chart.show()

    def process_data(self) -> None:
        """ Process data and sets X and Y axes labels """
        self.tm=[]
        self.y_min, self.y_max = (
            float("inf"),
            -float("inf"),
        )
        for index, row in self.df.iterrows():
            self.series.insert(0,QCandlestickSet(row['open'], row['high'], row['low'], row['close']))
            timestamp = str(int(row['timestamp'][8:10]))+'.'+str(row['timestamp'][5:7])+'.'
            self.tm.insert(0,timestamp)
            self.y_min = min(self.y_min, row['open'], row['high'], row['low'], row['close'])
            self.y_max = max(self.y_max, row['open'], row['high'], row['low'], row['close'])
            if index == self.market_days_shown-1: break
        
        
    def set_boundaries(self) -> None:
        """ Sets boundaries to the X and Y axes objects. """
        self.axisX.append(self.tm)
        self.axisY.setMax(self.y_max)
        self.axisY.setMin(self.y_min)
        self.axisY.setRange(self.y_min, self.y_max)
        self.axisY.show()


    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("StockChart v1")

        self.scroll_area = QScrollArea()
        self.vbox = QVBoxLayout()

        # STOCK BUTTON AND LINE EDIT
        self.stock_symbol_container = QWidget()
        self.stock_symbol_container.setLayout(QHBoxLayout())

        btn = QPushButton("Aktualizovat")
        btn.clicked.connect(self.update_stock)
        self.stock_symbol_container.layout().addWidget(btn)

        self.line_edit = QLineEdit(self.stock_ticker)
        self.line_edit.textChanged.connect(self.change_stock_ticker)
        self.stock_symbol_container.layout().addWidget(self.line_edit)
        re = QRegularExpression("[A-z]{1,11}")
        validator = QRegularExpressionValidator(re, self)
        self.line_edit.setValidator(validator)
        
        


        spinbox = QSpinBox()
        spinbox.setRange(15,100) # number of market days shown allowed
        spinbox.setValue(20) # set initial value
        spinbox.valueChanged.connect(self.change_market_days)
        self.stock_symbol_container.layout().addWidget(spinbox)

        self.vbox.addWidget(self.stock_symbol_container)

        self.download_data()
        self.create_series()
        self.process_data()
        self.create_rest()

        # VARIABLE GRID
        self.chartview = QChartView(self.chart)
        self.chartview.setObjectName("chartview")
        self.vbox.addWidget(self.chartview)

        # MAIN LAYOUT
        self.vbox.addWidget(QLabel("Vytvořil Lukáš Vítek, 2022"))
        self.setLayout(self.vbox)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    #app.setStyleSheet(qdarktheme.load_stylesheet())
    app.setStyleSheet(qdarktheme.load_stylesheet("light"))
    
    app_icon = QIcon()
    app_icon.addFile('icons/window_icon_16.png', QSize(16,16))
    app_icon.addFile('icons/window_icon_24.png', QSize(24,24))
    app_icon.addFile('icons/window_icon_32.png', QSize(32,32))
    app_icon.addFile('icons/window_icon_48.png', QSize(48,48))
    app_icon.addFile('icons/window_icon_256.png', QSize(256,256))
    app.setWindowIcon(app_icon)

    window = Window()
    window.show()
    window.resize(800, 600)
    window.move(300, 100)
    sys.exit(app.exec())