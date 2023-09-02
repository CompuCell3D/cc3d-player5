


class ConsoleWidgetBase:

    def set_player_main_widget(self, main_player_widget):
        raise NotImplemented

    def connect_close_cc3d_signal(self, callback):
        raise NotImplemented


    def emitCloseCC3D(self):
        raise NotImplemented


    def set_service_port_cc3d_sender(self, port:int):
        raise NotImplemented


    def is_qsci_based(self):
        raise NotImplemented