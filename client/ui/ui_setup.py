#ui.uisetup.py
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QButtonGroup, QTableWidget, QAbstractItemView
from handler.workout_handler import WorkoutHandler

class UISetupHelper:
    @staticmethod
    def profiles(main_window):
        main_window.count_up = 0
        main_window.tier = 0

        main_window.cur.execute("SELECT count(name) FROM user")
        cnt = int(main_window.cur.fetchall()[0][0])

        main_window.cur.execute("SELECT name, user_icon FROM user WHERE name IS NOT NULL")
        name = main_window.cur.fetchall()

        name_list = [n[0] for n in name]
        icon_list = [n[1] for n in name]

        buttons = [main_window.btn_profile1, main_window.btn_profile2, main_window.btn_profile3, main_window.btn_profile4]
        labels = [main_window.label_profile1, main_window.label_profile2, main_window.label_profile3, main_window.label_profile4]

        for btn, label in zip(buttons, labels):
            btn.setVisible(False)
            label.setText("")

        if cnt == 0:
            return

        icon_size = 200
        for i in range(cnt):
            pixmap = QPixmap()
            pixmap.loadFromData(icon_list[i])
            buttons[i].setIcon(QIcon(pixmap))
            buttons[i].setIconSize(QSize(icon_size, icon_size))
            labels[i].setText(name_list[i])
            buttons[i].setVisible(True)

        main_window.profile_cnt = cnt
        main_window.btn_plus_profile.setEnabled(cnt < 4)



    @staticmethod
    def buttons(main_window):
        main_window.btn_plus_profile.clicked.connect(main_window.plus_profile)

        # Main 
        main_window.btn_workout.setCheckable(True)
        main_window.btn_record.setCheckable(True)
        main_window.btn_rank.setCheckable(True)
        
        main_window.tab_group = QButtonGroup()
        main_window.tab_group.addButton(main_window.btn_workout)
        main_window.tab_group.addButton(main_window.btn_record)
        main_window.tab_group.addButton(main_window.btn_rank)

        main_window.btn_workout.clicked.connect(main_window.show_main)
        main_window.btn_record.clicked.connect(main_window.show_record)
        main_window.btn_rank.clicked.connect(main_window.show_rank)

        main_window.btn_workout.setChecked(True)

        main_window.btn_back2login.clicked.connect(main_window.back2login)
        main_window.btn_start.clicked.connect(lambda: WorkoutHandler.go2workout(main_window))
        main_window.btn_profile.clicked.connect(main_window.go2account)

        main_window.stackedWidget_big.setCurrentWidget(main_window.profile_page)
        main_window.stackedWidget_small.setCurrentWidget(main_window.main_page)

        main_window.btn_calendar.clicked.connect(main_window.go2calendar)
        main_window.btn_back2main.clicked.connect(main_window.back2main)
        
        # Workout
        main_window.btn_work_to_main.clicked.connect(main_window.back2main)
        main_window.btn_next.clicked.connect(main_window.handle_next_workout)       # for debugging 
        
        # Account 
        main_window.tab_group_2 = QButtonGroup()
        main_window.tab_group_2.addButton(main_window.btn_modify)
        main_window.tab_group_2.addButton(main_window.btn_goal)
        # main_window.tab_group_2.addButton(main_window.btn_todayrecord)
        main_window.tab_group_2.addButton(main_window.btn_config)
        main_window.btn_modify.setCheckable(True)
        main_window.btn_goal.setCheckable(True)
        # main_window.btn_todayrecord.setCheckable(True)
        main_window.btn_config.setCheckable(True)
        main_window.btn_modify.clicked.connect(main_window.show_modify)
        main_window.btn_goal.clicked.connect(main_window.show_goal)
        # main_window.btn_todayrecord.clicked.connect(main_window.show_todayrecord)
        main_window.btn_config.clicked.connect(main_window.show_config)
        main_window.btn_modify.setChecked(True)
        main_window.tableWidget.verticalHeader().setVisible(False)
        
        ## Account-modify
        # main_window.btn_select_profile_img_2.clicked.connect(lambda: select_icon(main_window.label_profile_icon_2, 
        #                                                                          main_window.btn_select_profile_img_2))
        # main_window.btn_profile_save_2.clicked.connect(lambda: profile_save(main_window))

        
        ## Account-config 
        main_window.btn_add_workout.clicked.connect(main_window.add_workout)
        main_window.btn_delete_workout.clicked.connect(main_window.delete_workout)
        main_window.btn_modify_workout.clicked.connect(main_window.modify_workout)
        main_window.tableWidget.setSelectionBehavior(QTableWidget.SelectRows)
        main_window.tableWidget.clicked.connect(main_window.click_tableWidget)
        main_window.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        main_window.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
 
        main_window.stackedWidget_small_2.setCurrentWidget(main_window.pg_modify)

        main_window.btn_back2main_2.clicked.connect(main_window.back2main)
    @staticmethod
    def button_stylers(main_window):
        main_window.day_icon.setPixmap(QPixmap("./image_folder/weights.png").scaled(30, 30))
        main_window.time_icon.setPixmap(QPixmap("./image_folder/clock.png").scaled(30, 30))
        main_window.count_icon.setPixmap(QPixmap("./image_folder/days.png").scaled(30, 30))
        
        main_window.lb_first.setPixmap(QPixmap("./image_folder/first.png").scaled(50, 50))
        # 회원정보 수정 Button
        main_window.btn_modify.setIcon(QIcon("./image_folder/Modify.png"))
        main_window.btn_modify.setIconSize(main_window.btn_modify.sizeHint())
        main_window.btn_modify.setStyleSheet("""
        QPushButton {
            border: none;
            padding: 0px;
            margin: 0px;
            text-align: left;                                 
        }
        """)
        
        # 목표설정 Button
        main_window.btn_goal.setIcon(QIcon("./image_folder/goal.png"))
        main_window.btn_goal.setIconSize(main_window.btn_goal.sizeHint())
        main_window.btn_goal.setStyleSheet("""
        QPushButton {
            border: none;
            padding: 0px;
            margin: 0px;
            text-align: left;            
        }
        """)
        # 운동설정 Button
        main_window.btn_config.setIcon(QIcon("./image_folder/gear.png"))
        main_window.btn_config.setIconSize(main_window.btn_config.sizeHint())
        main_window.btn_config.setStyleSheet("""
        QPushButton {
            border: none;
            padding: 0px;
            margin: 0px;
            text-align: left;            
        }
        """)
        # Back Button
        main_window.btn_back2login.setIcon(QIcon("./image_folder/Back.png"))
        main_window.btn_back2login.setIconSize(main_window.btn_plus_profile.sizeHint())
        
        # Back Button
        main_window.btn_back2main.setIcon(QIcon("./image_folder/Back.png"))
        main_window.btn_back2main.setIconSize(main_window.btn_plus_profile.sizeHint())

        # Plus Profile Button
        main_window.btn_plus_profile.setIcon(QIcon("./image_folder/plus.png"))
        main_window.btn_plus_profile.setIconSize(main_window.btn_plus_profile.sizeHint())
        main_window.btn_plus_profile.setStyleSheet("""
        QPushButton {
            border: 2px solid #ccc;
            background-color: white;
        }
        """)
        
        # Account Button
        main_window.btn_profile.setIcon(QIcon("./image_folder/User.png"))
        main_window.btn_profile.setIconSize(main_window.btn_plus_profile.sizeHint()*1.5)
        main_window.btn_profile.setStyleSheet("""
        QPushButton {
            border: 2px solid #ccc;
            background-color: SkyBlue;
        }
        """)

        # Calendar Button
        main_window.btn_calendar.setIcon(QIcon("./image_folder/Calendar.png"))
        main_window.btn_calendar.setIconSize(main_window.btn_calendar.sizeHint()*8)
        main_window.btn_calendar.setStyleSheet("""
        QPushButton {
            border: none;
            padding: 0px;
            margin: 0px;
        }
        """)

        # Routine list 
        main_window.routine_list.setStyleSheet("""
            QListWidget::item:selected {
                background-color: #87CEFA;   /* 연한 파랑 */
                color: black;
            }
        """)
