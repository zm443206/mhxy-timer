import re
import time
import random
import datetime
import winsound
import calendar
import threading
import tkinter as tk
from tkinter import ttk, messagebox

import pyttsx3
import mouse
import keyboard

__VERSION__ = 'v1.3.0'
__LAST_UPDATE__ = '2023-06-26'

class KeepClick:
    def __init__(self) -> None:
        self.__active = True
        self.__run = False
        
    def click(self):
        while True:
            time.sleep(0.1)
            if self.__active is True:
                while self.__run is True:
                    # 每秒约7 ~ 8次,符合正常按键手速极限,按键行为约5毫秒
                    time.sleep(random.uniform(0.12, 0.15))
                    mouse.click()
            else:
                print('收到程序关闭指令')
                return 
                
    def set_run(self, run: bool):
        self.__run = run

    def set_active(self, active: bool):
        self.__active = active

def run_keepclick():
    start_time = time.time()
    obj = KeepClick()
    threading.Thread(target=obj.click, daemon=True).start()

    keyboard.add_hotkey('F1', obj.set_run, args=(True, ))
    keyboard.add_hotkey('F2', obj.set_run, args=(False, ))
    while True:
        time.sleep(1)
        if time.time() - start_time > 100:
            obj.set_run(False)
            obj.set_active(False)
            return

class Main:
    def __init__(self, options):
        self.everyday = ({'帮派强盗': '12:30:00', '门派闯关': '21:00:00', '竞技场活动': '22:00:00'},
                        {'帮派百草谷': '12:30:00', '帮派答题': '20:20:00', '帮派竞赛': '21:00:00'},
                        {'九黎演武': '12:15:00', '召唤灵乐园': '21:00:00', '风云竞技场': '22:00:00'},
                        {'帮派百草谷': '12:30:00', '帮派答题': '20:20:00', '帮派竞赛': '21:00:00'},
                        {'帮派迷阵': '12:00:00', '勇闯迷魂塔': '19:00:00', '剑会群英': '20:00:30'},
                        {'不周山神': '11:00:00', '剑会群英': '12:00:30', '小猪快跑': '12:05:00', 
                         '科举会试1': '13:00:00', '科举|不周': '15:00:00', '不周山神': '19:00:00', 
                         '科举会试3': '20:00:00', '决战九华山': '21:00:00', '帮派车轮战': '22:00:00', '不周山神': '23:00:00'},
                        {'不周山神': '11:00:00', '剑会群英': '12:00:30', '帮派秘境': '12:30:00', '不周山神': '15:00:00', 
                         '擂台大挑战': '17:00:00', '梦幻迷城': '18:30:00', '不周山神': '19:00:00', '比武大会': '21:00:00', 
                         '比武大会-结束': '22:20:00', '不周山神': '23:00:00'}, )
        

        self.disha = {'地煞1': '09:30:30', '地煞2': '11:30:30', '地煞3': '13:30:30', '地煞4': '15:30:30',
                      '地煞5': '17:30:30', '地煞6': '19:30:30', '地煞7': '22:30:30', '地煞8': '23:30:30'}
        
        self.yuanchen = {}
        for i in range(24):
            self.yuanchen['元辰' + str(i)] = '{}:00:15'.format(str(i).zfill(2))

        self.hufu = {'上古灵符1': '10:10:00', '上古灵符2': '16:10:00', 
                     '上古咒符1': '12:10:00', '上古咒符2': '18:10:00', 
                     '上古护符1': '14:10:00', '上古护符2': '20:10:00'}
        
        # ==================初始化活动内容==================
        self.new_dict = {}

        for i, b in enumerate(options):
            if b:
                match i:
                    case 0:
                        self.new_dict.update(self.everyday[time.localtime().tm_wday])

                        # 每月的最后一个星期一(武神坛活动)
                        month_calendar = calendar.monthcalendar(datetime.date.today().year, datetime.date.today().month)
                        last_monday = month_calendar[-1][0]
                        if datetime.date.today().day == last_monday:
                            self.new_dict.update({'武神坛庆功游行': '20:00:00', '武神坛在线抽奖': '20:20:00'})

                        # 每月的最后一个周六(科举殿试)
                        month_calendar = calendar.monthcalendar(datetime.date.today().year, datetime.date.today().month)
                        if month_calendar[-1][5] == 0:
                            last_saturday = month_calendar[-2][5]
                        else:
                            last_saturday = month_calendar[-1][5]
                        if datetime.date.today().day == last_saturday:
                            self.new_dict['科举殿试'] = '20:15:00'
                    case 1:
                        self.new_dict.update(self.disha)
                    case 2:
                        self.new_dict.update(self.yuanchen)
                    case 3:
                        self.new_dict.update(self.hufu)

        self.new_list = sorted(self.new_dict.items(), key=lambda k: k[1])
        self.new_list = list(filter(lambda item: item[1] > time.strftime('%H:%M:%S'), self.new_list))

        # ==================初始化语音引擎==================
        self.speak = self.say()
        next(self.speak)

    
    def play(self, text1: tk.StringVar, text2: tk.StringVar, option: tk.BooleanVar):
        self.speak.send('梦幻手游,时间管理大师,已启动')
        while True:
            self.tx1 = self.new_list[0]
            text1.set('[{:<}] ----- {}'.format((re.findall('\D+', self.tx1[0]))[0], self.tx1[1]))
            
            self.tx2 = self.new_list[1:5]
            text2.set('\n'.join('[{:<}] ----- {}'.format((re.findall('\D+', item))[0], tm) for item, tm in self.tx2))
            
            try:
                name, tm = self.new_list.pop(0)
            except IndexError:
                time.sleep(10)
                self.speak.send('活动已全部结束')
                text1.set('--活动已全部结束--')
                self.speak.close()
                break
            else:
                get_diff_time = self.diff_time(tm)
                if get_diff_time > 180:
                    time.sleep(get_diff_time - 180)
                    self.speak.send(('距离{}, 还有三分钟'.format((re.findall('\D+', name))[0])).replace('地', '弟'))

                get_diff_time = self.diff_time(tm)
                if get_diff_time > 60:
                    time.sleep(get_diff_time - 60)
                    self.speak.send(('距离{}, 还有一分钟'.format((re.findall('\D+', name))[0])).replace('地', '弟'))   

                get_diff_time = self.diff_time(tm)
                if get_diff_time > 10:
                    if result := ('上古' in name and option.get() is True):
                        time.sleep(get_diff_time - 9)
                    else:
                        time.sleep(get_diff_time - 4)

                    for _ in range(4):
                        t1 = time.perf_counter()
                        winsound.Beep(523, 200)
                        time.sleep(t1 + 1 - time.perf_counter())
                    else:
                        winsound.Beep(988, 988)

                    if result is True:
                        time.sleep(1)
                        self.speak.send('鼠标连点器, 激活')
                        run_keepclick()
                        time.sleep(1)
                        self.speak.send('鼠标连点器, 关闭')



    def diff_time(self, end_time: str) -> int:
        '''
        返回活动时间与当前时间的差 -> 秒
        '''
        end_time = datetime.datetime.combine(datetime.date.today(), datetime.time(*(map(int, end_time.split(':')))))
        local_time = datetime.datetime.today()
        time_delta = end_time - local_time
        return time_delta.seconds
    
    def say(self):
        engine = pyttsx3.init()
        engine.setProperty('voice', 'zh')
        engine.setProperty('volume', 0.9)
        engine.setProperty('rate', 120)
        while True:
            sy = yield
            engine.say(sy)
            engine.runAndWait()


class MainForm:
    def __init__(self):
        # 时间显示防多次激活互斥
        self.mutex = False
        # 右键置顶, 标签切换flag
        self.mutex_2 = False

        self.root = tk.Tk()
        self.root.title('<梦幻手游>时间管理大师 {}'.format(__VERSION__))
        self.root.geometry('{}x{}+{}+{}'.format(450, 300, (self.root.winfo_screenwidth()-450)//2, (self.root.winfo_screenheight()-330)//2))
        self.root.resizable(width=False, height=False)
        self.root.protocol('WM_DELETE_WINDOW', func=self.close_window_event)

        self.top_most_menu = tk.Menu(tearoff=False)
        self.top_most_menu.add_command(label='置顶', command=self.top_most_menu_event)
        self.root.bind('<Button-3>', func=lambda event: self.top_most_menu.post(event.x_root, event.y_root))

        # No.1 勾选区
        self.frame_1 = ttk.Frame(self.root)
        self.frame_1.place(x=0, y=0)

        self.label_1 = ttk.Label(self.frame_1, text='勾选要提醒的项目', background='#2d2d2d', foreground='#ffffff', font=('微软雅黑', 13))
        self.label_1.grid(row=0, column=0, columnspan=4, sticky='w')

        self.check_button_value = [(0, '日常', tk.BooleanVar(value=True)), (1, '地煞', tk.BooleanVar(value=False)), (2, '元辰', tk.BooleanVar(value=False)), (3, '护符', tk.BooleanVar(value=False))]
        self.check_button_obj = []
        for index, item, var in self.check_button_value:
            self.check_button_1 = ttk.Checkbutton(self.frame_1, text=item, onvalue=True, offvalue=False, variable=var)
            self.check_button_1.grid(row=1, column=index)
            self.check_button_obj.append(self.check_button_1)


        # No.2 数显区
        self.frame_2 = ttk.Frame(self.root)
        self.frame_2.place(x=225, y=0)

        self.radio_button_var = tk.BooleanVar(value=False)
        self.radio_button_2_1 = ttk.Radiobutton(self.frame_2, text='显示', value=True, variable=self.radio_button_var, command=self.radio_button_event)
        self.radio_button_2_2 = ttk.Radiobutton(self.frame_2, text='隐藏', value=False, variable=self.radio_button_var)
        self.radio_button_2_1.grid(row=0, column=0)
        self.radio_button_2_2.grid(row=1, column=0)

        self.time_label_content = tk.StringVar(value='- -: - -: - -')
        self.time_label = ttk.Label(self.frame_2, textvariable=self.time_label_content, font=('ink free', 28), justify='right')
        self.time_label.grid(row=0, column=1, rowspan=2, padx=(10, 0))


        # No.3 启动
        self.frame_3 = ttk.Frame(self.root)
        self.frame_3.place(x=0, y=52)

        self.start_button = ttk.Button(self.frame_3, text='启动', width=62, cursor='hand2', command=self.start_button_event)
        self.start_button.pack(anchor='n', fill='x', pady=(5, 5))

        ttk.Separator(self.frame_3, orient='horizontal').pack(fill='x')

        # No.4
        # 左下记事本
        self.frame_4 = ttk.Frame(self.root)
        self.frame_4.place(x=0, y=92, width=215, height=200)

        self.check_button_4_var = tk.BooleanVar(value=True)
        self.check_button_4_1 = ttk.Checkbutton(self.frame_4, text='鼠标连点器', onvalue=True, offvalue=False, variable=self.check_button_4_var)
        self.check_button_4_1.pack(side='top', anchor='nw')
        self.label_4_1 = ttk.Label(self.frame_4, text='此功能只在勾选<护符>项后才有效\n<F1>: 运行 <F2>: 停止\n功能激活时间为护符开始后的100s内\n其它时间均不起作用')
        self.label_4_1.pack(side='top', anchor='nw', fill='x')

        # No.5
        self.frame_5 = ttk.Frame(self.root)
        self.frame_5.place(x=225, y=92, width=215, height=200)
        self.frame_5_1 = ttk.Frame()
        self.frame_5_2 = ttk.Frame()

        self.notebook = ttk.Notebook(self.frame_5)
        self.notebook.add(self.frame_5_1, text='进行时')
        self.notebook.add(self.frame_5_2, text='临时闹钟')
        self.notebook.pack(expand=True, fill='both')

        self.label_5_1_content = tk.StringVar(value='...')
        self.label_5_1 = ttk.Label(self.frame_5_1, textvariable=self.label_5_1_content, font=('微软雅黑', 12, 'bold'), foreground='#ff0000', relief='solid', width=21, anchor='w', justify='left')
        self.label_5_1.pack(side='top', anchor='w')

        self.label_5_2_content = tk.StringVar(value='...')
        self.label_5_2 = ttk.Label(self.frame_5_1, textvariable=self.label_5_2_content, font=('微软雅黑', 12), justify='left', anchor='w')
        self.label_5_2.pack(side='top', anchor='w')
        

        self.root.mainloop()

    def top_most_menu_event(self):
        if self.mutex_2 is False:
            self.root.attributes('-topmost', 1)
            self.top_most_menu.entryconfig(0, label='取消置顶')
            self.mutex_2 = True
        else:
            self.root.attributes('-topmost', 0)
            self.top_most_menu.entryconfig(0, label='置顶')
            self.mutex_2 = False

    def close_window_event(self):
        if self.start_button.instate((tk.DISABLED, )):
            if messagebox.askyesno('强制关闭', '程序正在运行,是否强制关闭?\n'*3):
                self.root.destroy()
        else:
            self.root.destroy()

    def radio_button_event(self):
        def time_loop():
            if self.radio_button_var.get() is True:
                self.time_label_content.set(time.strftime('%H:%M:%S'))
                self.root.after(1000, time_loop)
            else:
                self.mutex = False
                self.time_label_content.set('- -: - -: - -')

        if self.mutex is False:
            self.mutex = True
            return time_loop()
        else:
            print('重复点击忽略')

    def start_button_event(self):
        if not any((i[2].get() for i in self.check_button_value)):
            messagebox.showwarning('启动了个寂寞', '您未选择任何项???\n启动了个寂寞~~')
            return
        else:
            for obj in self.check_button_obj:
                obj.config(state=tk.DISABLED)
            
            self.start_button.config(state=tk.DISABLED, text=' 运 行 中 '.center(50, '-'))
            
            app = Main((i[2].get() for i in self.check_button_value))
            self.td = threading.Thread(target=app.play, args=(self.label_5_1_content, self.label_5_2_content, self.check_button_4_var), daemon=True)
            self.td.start()


if __name__ == '__main__':
    MainForm()