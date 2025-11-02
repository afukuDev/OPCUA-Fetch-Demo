# run_manager.py
"""
Manager GUI to start/stop and monitor three scripts:
  1) OPC UA server (default: opcua_server.py)
  2) vue_flask_api.py
  3) python_opcua_datafetch.py

Place this file in the same folder as those scripts or edit the path variables below.
"""

import os
import sys
import subprocess
import threading
import queue
import time
import signal
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# -------------------------
# CONFIG: 修改這裡以配合你的檔名 / 路徑
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 預設檔名（若你的檔名不同或在其他資料夾，請改這裡）
# OPCUA_SERVER_SCRIPT = os.path.join(BASE_DIR, "opcua_server.py") # Real Sensor Data on Opcua
OPCUA_SERVER_SCRIPT = os.path.join(BASE_DIR, "OPCUA_local_RandomValue_serve.py") # Random Value Data on Opcua
VUE_FLASK_SCRIPT = os.path.join(BASE_DIR, "vue_flask_api.py")
DATA_FETCH_SCRIPT = os.path.join(BASE_DIR, "python_opcua_datafetch.py")

# -------------------------
# 內部使用（不要改）
# -------------------------
PYTHON_EXE = sys.executable
READ_INTERVAL_MS = 200   # GUI 每多少毫秒檢查 queue 並更新 terminal
LOG_LINE_PREFIX = "[{time}] "

# -------------------------
# Process wrapper
# -------------------------
class ManagedProcess:
    def __init__(self, label, script_path):
        self.label = label
        self.script = script_path
        self.proc = None
        self.stdout_thread = None
        self.queue = queue.Queue()
        self.alive_lock = threading.Lock()

    def is_running(self):
        return self.proc is not None and self.proc.poll() is None

    def start(self):
        if self.is_running():
            return True
        if not os.path.exists(self.script):
            raise FileNotFoundError(f"Script not found: {self.script}")
        # spawn the script with merged stdout/stderr for simpler reading
        try:
            # optional: ensure child uses utf-8 output (可解 emoji / 編碼問題)
            env = os.environ.copy()
            env.setdefault("PYTHONIOENCODING", "utf-8")

            self.proc = subprocess.Popen(
                [PYTHON_EXE, self.script],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                universal_newlines=True,
                start_new_session=True,  # gives process its own session
                env=env
            )
        except Exception as e:
            self.proc = None
            raise

        # start reader thread
        self.stdout_thread = threading.Thread(target=self._reader_thread, daemon=True)
        self.stdout_thread.start()
        return True

    def _reader_thread(self):
        """Read lines from proc.stdout and push into queue"""
        if not self.proc or not self.proc.stdout:
            return
        try:
            for line in self.proc.stdout:
                ts = time.strftime("%H:%M:%S")
                self.queue.put((ts, line.rstrip("\n")))
        except Exception:
            pass
        finally:
            # indicate process ended; returncode may be None if abnormal
            rc = None
            try:
                rc = self.proc.returncode
            except Exception:
                rc = None
            self.queue.put((time.strftime("%H:%M:%S"), f"[Process exited: returncode={rc}]"))

    def terminate(self, timeout=2.0):
        if not self.proc:
            return
        try:
            if self.is_running():
                try:
                    self.proc.terminate()
                except Exception:
                    pass
                # wait a bit
                try:
                    self.proc.wait(timeout=timeout)
                except Exception:
                    try:
                        self.proc.kill()
                    except Exception:
                        pass
        finally:
            self.proc = None

# -------------------------
# GUI App
# -------------------------
class ManagerApp:
    def __init__(self, root):
        self.root = root
        root.title("Process Manager — OPCUA / Flask / DataFetch")
        root.geometry("1100x720")

        # create managed processes
        self.procs = {
            "opcua": ManagedProcess("OPC UA Server", OPCUA_SERVER_SCRIPT),
            "vue": ManagedProcess("vue_flask_api", VUE_FLASK_SCRIPT),
            "data": ManagedProcess("python_opcua_datafetch", DATA_FETCH_SCRIPT),
        }

        self._build_ui()
        # schedule periodic terminal update
        self._refresh_terminals()

        # ensure clean shutdown
        root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        frm = ttk.Frame(self.root)
        frm.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Top: three control panels horizontally
        top = ttk.Frame(frm)
        top.pack(fill=tk.X, padx=4, pady=4)

        # Create a control panel for each process
        for key, mp in self.procs.items():
            self._create_control_card(top, key, mp)

        # Bottom: three terminal panes
        bottom = ttk.Frame(frm)
        bottom.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self.term_texts = {}
        for i, key in enumerate(["opcua", "vue", "data"]):
            card = ttk.Labelframe(bottom, text=f"{self.procs[key].label} Output")
            card.grid(row=0, column=i, sticky="nsew", padx=4, pady=4)
            bottom.grid_columnconfigure(i, weight=1)

            txt = scrolledtext.ScrolledText(card, wrap=tk.NONE, height=18)
            txt.pack(fill=tk.BOTH, expand=True)
            txt.configure(state=tk.DISABLED)

            # 設定顏色 tags（可依需求修改顏色）
            txt.tag_configure("green", foreground="green")
            txt.tag_configure("yellow", foreground="orange")
            txt.tag_configure("red", foreground="red")
            txt.tag_configure("default", foreground="black")

            self.term_texts[key] = txt

    def _create_control_card(self, parent, key, mp: ManagedProcess):
        card = ttk.Frame(parent, relief=tk.RIDGE, borderwidth=2, padding=(8,8))
        card.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=6)

        title = ttk.Label(card, text=mp.label, font=("Helvetica", 11, "bold"))
        title.pack(anchor=tk.W)

        desc = ttk.Label(card, text=f"script: {os.path.basename(mp.script)}", foreground="gray30")
        desc.pack(anchor=tk.W, pady=(0,6))

        # status indicator (canvas circle)
        status_frm = ttk.Frame(card)
        status_frm.pack(anchor=tk.W, pady=(0,6))
        tk.Label(status_frm, text="狀態:").pack(side=tk.LEFT)
        canvas = tk.Canvas(status_frm, width=18, height=18, highlightthickness=0)
        canvas.pack(side=tk.LEFT, padx=(4,10))
        # draw circle
        circle = canvas.create_oval(2,2,16,16, fill="red")
        # store references
        mp._ui = {"canvas": canvas, "circle": circle}

        # start/stop toggle button
        btn = ttk.Button(card, text="Start", command=lambda k=key: self._toggle_process(k))
        btn.pack(anchor=tk.W, pady=(0,6))
        mp._ui["button"] = btn

        # small note
        note = ttk.Label(card, text="說明: 開啟後可在下方 terminal 看到即時輸出。", font=("Arial", 9))
        note.pack(anchor=tk.W)

    def _update_indicator(self, key):
        mp = self.procs[key]
        canvas = mp._ui["canvas"]
        circle = mp._ui["circle"]
        if mp.is_running():
            canvas.itemconfig(circle, fill="green")
            mp._ui["button"].configure(text="Stop")
        else:
            canvas.itemconfig(circle, fill="red")
            mp._ui["button"].configure(text="Start")

    def _toggle_process(self, key):
        mp = self.procs[key]
        if mp.is_running():
            # stop
            mp.terminate()
            # push message to terminal queue
            mp.queue.put((time.strftime("%H:%M:%S"), "[Termiated_by_user] 使用者終止程式"))
            self._update_indicator(key)
        else:
            # start
            try:
                mp.start()
                mp.queue.put((time.strftime("%H:%M:%S"), "[Started]"))
            except FileNotFoundError as e:
                messagebox.showwarning("啟動失敗", f"{mp.label} 無法啟動：\n{e}")
            except Exception as e:
                messagebox.showwarning("啟動失敗", f"{mp.label} 啟動過程發生錯誤：\n{e}")
                # ensure it's not left in partially started state
                try:
                    mp.terminate()
                except Exception:
                    pass
            finally:
                self._update_indicator(key)

    def _classify_tag_for_line(self, line_text: str) -> str:
        """
        根據 line 的開頭回傳 tag 名稱：'green' / 'yellow' / 'red' / 'default'
        注意：line_text 是不包含 timestamp 的原始 line
        """
        # 先 trim 左右空白（避免前導空白影響判斷）
        s = line_text.lstrip()
        if s.startswith("[Feedback]") or s.startswith("[OK]") or s.startswith("[Started]"):
            return "green"
        if s.startswith("[Warning]") or s.startswith("[Waiting]"):
            return "yellow"
        if s.startswith("[Error]") or s.startswith("[Termiated_by_user]") or s.startswith("[Terminated_by_user]") or s.startswith("[Stopped"):
            return "red"
        return "default"

    def _refresh_terminals(self):
        # pull from each process queue and append to respective text widget
        for key, mp in self.procs.items():
            txt = self.term_texts[key]
            updated = False
            while True:
                try:
                    ts, line = mp.queue.get_nowait()
                except queue.Empty:
                    break
                # append to text and apply color tag based on message prefix (line itself, not timestamp)
                tag = self._classify_tag_for_line(line)

                txt.configure(state=tk.NORMAL)
                # insert full string with timestamp
                txt.insert(tk.END, LOG_LINE_PREFIX.format(time=ts) + line + "\n")
                # compute the start/end of the last inserted line then add tag
                try:
                    start = txt.index('end-1c linestart')
                    end = txt.index('end-1c lineend')
                    txt.tag_add(tag, start, end)
                except Exception:
                    # fallback: apply tag to whole text if indexing fails
                    txt.tag_add(tag, "1.0", tk.END)

                txt.see(tk.END)
                txt.configure(state=tk.DISABLED)
                updated = True
            # update indicator based on process state
            self._update_indicator(key)
        # schedule next check
        self.root.after(READ_INTERVAL_MS, self._refresh_terminals)

    def _on_close(self):
        if messagebox.askokcancel("離開", "確定要結束管理程式並終止所有子程序嗎？"):
            # terminate children
            for key, mp in self.procs.items():
                try:
                    if mp.is_running():
                        mp.terminate(timeout=1.0)
                except Exception:
                    pass
            # small pause to allow cleanup
            time.sleep(0.2)
            self.root.destroy()

# -------------------------
# Entrypoint
# -------------------------
def main():
    # quick existence check and show warning but allow GUI to run
    for key, path in (("OPC UA Server", OPCUA_SERVER_SCRIPT),
                      ("vue_flask_api", VUE_FLASK_SCRIPT),
                      ("data_fetch", DATA_FETCH_SCRIPT)):
        if not os.path.exists(path):
            print(f"⚠️ Warning: {key} script not found at: {path}")
    root = tk.Tk()
    app = ManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
