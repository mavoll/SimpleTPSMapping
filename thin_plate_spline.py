import cv2
import imutils
from threading import Thread
from collections import deque
import colorsys
import csv

import numpy as np
import sys
from tkinter import Button
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askopenfilenames
from tkinter.filedialog import asksaveasfilename
from tkinter import Label
from tkinter import messagebox
from tkinter import Tk
from tkinter import ttk
from tkinter import Toplevel
from tkinter import Entry
from tkinter import END

import pairs_window

class App(object):
  
    def __init__(self):
                    
        self.alpha = 0.5
        self.rotate_grade = 0
        self.scale_width = 100
        self.move_x = 0
        self.move_y = 0    
      
        self.image = None
        self.ref_image = None
        self.clone = None
      
        self.scale_factor = 0.7
        self.root = Tk()
        self.opencv_thread = None
        
        self.refPt = []
        self.inter_line_counter = 0
        
        self.pairs_window = None
        
        self.lat_top_left = 53.549933
        self.long_top_left = 9.995458
        self.lat_bottom_right = 53.548746
        self.long_bottom_right = 9.998395
        
        self.tracks_by_files = []
        
    def run(self):

        self.root.wm_title("Select actions:")
        self.root.resizable(width=False, height=False)
        self.root.geometry('{}x{}'.format(250, 525))
        self.root.attributes("-topmost", True)
        
        labelTop = Label(self.root,
                         text="Choose image scale factor:")
        labelTop.pack(side="top", padx="10", pady="5")
        
        comboExample = ttk.Combobox(self.root,
                                    values=[
                                        0.5,
                                        0.6,
                                        0.7,
                                        0.8,
                                        0.9,
                                        1.0])

        comboExample.current(2)
        comboExample.state(['readonly'])
        comboExample.bind("<<ComboboxSelected>>", self.set_scale_factor)
        comboExample.pack(side="top", padx="10", pady="5")
        
          
        btn1 = Button(self.root, 
                      text="1. Select images \n(perspective image and \nreference map image)", 
                      command=self.open_image)
        btn1.pack(side="top", fill="both", expand="yes", padx="10", pady="5")
        
        labelTop = Label(self.root,
                         text="2. Adjust the reference image \n using the sliders and \n fit it into background image")
        labelTop.pack(side="top", padx="10", pady="5")
       
        labelTop = Label(self.root,
                         text="3. Set pairs of points \n (using the mouse) \n \n or")
        labelTop.pack(side="top", padx="10", pady="5")
        
        btn11 = Button(self.root, 
                      text="3. Open point pairs from file", 
                      command=self.open_pairs)
        btn11.pack(side="top", fill="both", expand="yes", padx="10", pady="5")
        
        btn81 = Button(self.root, 
                      text="4. Perform TPS \n transformation and warping", 
                      command=self.do_tps_trans_and_warp)
        btn81.pack(side="top", 
                  fill="both", 
                  expand="yes", 
                  padx="10", 
                  pady="5")
        
        btn84 = Button(self.root, 
                      text="5. Enter reference coordinates \n (lat, long)", 
                      command=self.ask_for_ref_coordinates)
        btn84.pack(side="top", 
                  fill="both", 
                  expand="yes", 
                  padx="10", 
                  pady="5")
                
        btn82 = Button(self.root, text="6. Open tracking result \n files to transform", 
                      command=self.open_tracks)
        btn82.pack(side="top", fill="both", expand="yes", padx="10", pady="5")
        
        btn83 = Button(self.root, 
                      text="7. Transform tracking results \n ( (x,y) to (lat, long) ) \n and save them to csv file", 
                      command=self.transform_to_geo)
        btn83.pack(side="top", fill="both", expand="yes", padx="10", pady="5")
                
        self.root.protocol("WM_DELETE_WINDOW", App.on_closing)
        self.root.mainloop()

        cv2.destroyAllWindows()
        sys.exit()
        
    def set_scale_factor(self, event=None):

        if event is not None:
            self.scale_factor = float(event.widget.get())

    def open_image(self):

        options = {}
        options['filetypes'] = [('Image file', '.jpg'), ('Image file', '.jpeg')]
        options['defaultextension'] = "jpg"
        options['title'] = "Choose image"

        filename = askopenfilename(**options)

        if filename:
            
            self.image = cv2.imread(filename)
            h = int(self.image.shape[0] * self.scale_factor)
            w = int(self.image.shape[1] * self.scale_factor)
            self.image = cv2.resize(self.image, (w, h))
            self.clone = self.image.copy()
        
            self.pixel_points = []
            self.fix_points = []
            self.refPt = []
            self.inter_line_counter = 0
            self.pairs_window = None
            
            self.alpha = 0.5
            self.rotate_grade = 0
            self.scale_width = 100
            
            self.tracks_by_files = []
            
            self.open_ref_image()
            
            if self.opencv_thread is None:
                self.opencv_thread = Thread(target=self.show_image)
                self.opencv_thread.daemon = True
                self.opencv_thread.start()
            else:
                self.draw()

    def open_ref_image(self):

        options = {}
        options['filetypes'] = [('Image file', '.jpg'), ('Image file', '.jpeg')]
        options['defaultextension'] = "jpg"
        options['title'] = "Choose ref image"

        filename = askopenfilename(**options)

        if filename:
             
            self.ref_image = cv2.imread(filename, -1)            
            h = int(self.ref_image.shape[0] * self.scale_factor)
            w = int(self.ref_image.shape[1] * self.scale_factor)
            
            self.ref_image = cv2.resize(self.ref_image, (w, h))
            
            d_h = self.image.shape[0] - h
            d_w = self.image.shape[1] - w
                
            if (d_h > d_w and d_h > 0) or (d_h > d_w and d_h <= 0):
                self.ref_image = imutils.resize(self.ref_image, width=self.image.shape[1])
            else:
                self.ref_image = imutils.resize(self.ref_image, height=self.image.shape[0])
            
            self.move_x = int(self.ref_image.shape[1] / 2)
            self.move_y = int(self.ref_image.shape[0] / 2)

    def open_tracks(self):

        if self.image is not None:

            options = {}
            options['filetypes'] = [('Text file', '.txt'),
                                    ('Comma separated', '.csv'), ('All files', '*')]
            options['defaultextension'] = "txt"
            options['title'] = "Choose tracking results file(s)"

            mes = "If you choose more than one tracking file, make sure that those\
                files are named in a manner that make them sortable! It is important\
                in order to associate all frames with its correct creation time!"
            messagebox.showinfo("Caution!", mes)

            filenames = askopenfilenames(**options)

            if filenames:

                lst = list(filenames)
                self.path_to_tracking_res = sorted(lst)
                self.tracks_by_files = []     
                self.draw_all_tracks()

        else:
            messagebox.showinfo("No image selected", "Please select an image first!")
            
    def show_image(self):

        cv2.namedWindow('image', cv2.WINDOW_AUTOSIZE)
        cv2.moveWindow('image', 0, 0)
        cv2.setMouseCallback('image', self.set_points_callback)
                    
        self.start_processing()

        cv2.destroyAllWindows()
        self.opencv_thread = None

    def start_processing(self):
        
        if self.image is not None:
                        
            try:                    
                trackbar_name = 'Alpha x %d' % 100
                cv2.createTrackbar(trackbar_name, 'image' , 
                                   int(self.alpha * 100), 
                                   100, 
                                   self.on_trackbar_alpha)
                
                trackbar_name2 = 'Width x %d' % 100
                cv2.createTrackbar(trackbar_name2, 'image' , 
                                   self.scale_width, 
                                   500, 
                                   self.on_trackbar_size)
                
                trackbar_name3 = 'Rotate x %d' % 100
                cv2.createTrackbar(trackbar_name3, 'image' , 
                                   self.rotate_grade, 360, 
                                   self.on_trackbar_rotate)

                trackbar_name4 = 'Move x %d' % 100
                cv2.createTrackbar(trackbar_name4, 'image' , 
                                   self.move_x, 
                                   self.ref_image.shape[1], 
                                   self.on_trackbar_move_x)
                
                trackbar_name5 = 'Move y %d' % 100
                cv2.createTrackbar(trackbar_name5, 'image' , 
                                   self.move_y, 
                                   self.ref_image.shape[0], 
                                   self.on_trackbar_move_y)                                   
                
                self.draw()
                
                cv2.waitKey(0)                

            except Exception:

                #continue
                e = sys.exc_info()[0]
                messagebox.showinfo("Error processing file", e)
                raise
    
    def set_points_callback(self, event, x, y, flags, param):

        if event == cv2.EVENT_LBUTTONDOWN:
            if self.refPt:
                self.refPt.append((x, y))
            else:
                self.refPt = [(x, y)]

        elif event == cv2.EVENT_LBUTTONUP:
            if self.refPt[-1] != (x, y):
                #More lists than needed but too lazy to change it :)
                self.refPt.append((x, y))                
                self.pixel_points.append(self.refPt[self.inter_line_counter])
                self.fix_points.append(self.refPt[self.inter_line_counter + 1])
                self.inter_line_counter += 2
                self.draw()
                self.open_update_pairs_window()
            else:
                self.refPt.pop()
                self.draw()

    def put_points_and_line_on_image(self, img, point1, point2, pair_id):

        cv2.line(img, point1, point2, (0, 255, 0), 2)
        cv2.putText(img,
                    "p1" + str(point1),
                    (point1[0] - 60, point1[1]),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.3,
                    (0, 0, 255),
                    1)
        cv2.putText(img,
                    "p2" + str(point2),
                    (point2[0] - 60, point2[1]),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.3,
                    (0, 0, 255),
                    1)

        tmpd = App.get_line_mid_point(point1, point2)
        cv2.putText(img,
                    str(pair_id),
                    (int(tmpd[0]) - 20, int(tmpd[1])),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    2)
        
        return img
                        
    def do_tps_trans_and_warp(self):        
        
        if len(self.pixel_points) == len(self.fix_points) and len(self.pixel_points) >= 3:   
            
            matches = list()
            for i in range(0, len(self.pixel_points)):            
                matches.append(cv2.DMatch(i,i,0))
            
            pixel_points = np.float32(self.pixel_points).reshape(1, -1, 2)
            fix_points = np.float32(self.fix_points).reshape(1, -1, 2)
            
            tps_transformer = cv2.createThinPlateSplineShapeTransformer(0)
                                        
            tps_transformer.estimateTransformation(pixel_points, fix_points, matches)        
            ret, output = tps_transformer.applyTransformation(pixel_points)
            
            #image = tps_transformer.warpImage(self.image, cv2.INTER_LINEAR)
            
            #image = np.zeros((self.image.shape[0],self.image.shape[1],1), np.uint8)
            image = self.image.copy()
            for i in range(0, int(self.image.shape[1] / 10) + 1):           
                cv2.line(image, (10 * i, 0), (10 * i, self.image.shape[0]), (255,255,255), 1)
                
            for i in range(0, int(self.image.shape[0] / 10) + 1):           
                cv2.line(image, (0, 10 * i), (self.image.shape[1], 10 * i), (255,255,255), 1)
                
            image = tps_transformer.warpImage(image, cv2.INTER_LINEAR)
            print(image)
            
#            INTER_NEAREST 	
#            nearest neighbor interpolation
#            
#            INTER_LINEAR 	
#            bilinear interpolation
#            
#            INTER_CUBIC 	
#            bicubic interpolation
#            
#            INTER_AREA 	
#            resampling using pixel area relation.
#            
#            It may be a preferred method for image decimation, as it gives moire'-free results. But when the image is zoomed, it is similar to the INTER_NEAREST method.
#            
#            INTER_LANCZOS4 	
#            Lanczos interpolation over 8x8 neighborhood.
#            
#            INTER_LINEAR_EXACT 	
#            Bit exact bilinear interpolation.
#            
#            INTER_MAX 	
#            mask for interpolation codes
#            
#            WARP_FILL_OUTLIERS 	
#            flag, fills all of the destination image pixels.
#            
#            If some of them correspond to outliers in the source image, they are set to zero
#            
#            WARP_INVERSE_MAP 	
#            flag, inverse transformation
#            
#            For example, linearPolar or logPolar transforms:
#            
#            flag is not set: dst(ρ,ϕ)=src(x,y)
#            flag is set: dst(x,y)=src(ρ,ϕ)
            
            cv2.imshow("image", image)
        
        else:
            messagebox.showinfo("Not enough points!", "Please set at least 3 point pairs!")
    
    def transform_to_geo(self):
        
        tracks_by_files_transformed = self.tracks_by_files.copy()
        
        
        self.draw_tracks(self.ref_image, tracks_by_files_transformed)
        App.save_tracks(tracks_by_files_transformed)
        
    def open_update_pairs_window(self):
        
        if self.pairs_window is None:            
            self.pairs_window = pairs_window.PairsWindow(self)
        
        else:
            self.pairs_window.update_gui()
            
    def open_pairs(self):
        
        if self.image is not None:

            options = {}
            options['filetypes'] = [('Text file', '.txt'),
                                    ('Comma separated', '.csv'), ('All files', '*')]
            options['defaultextension'] = "txt"
            options['title'] = "Choose pairs file"

            filenames = askopenfilename(**options)

            if filenames:
                with open(filenames, 'r') as csv_file:

                    csv_reader = csv.reader(csv_file, delimiter=',')
                    refPt = list(csv_reader)
                    self.refPt = [eval(refPt[0][i]) for i in range(0, len(refPt[0]))]
                
                #More lists than needed but too lazy to change it :)
                self.pixel_points = self.refPt[0::2]
                self.fix_points = self.refPt[1::2]                
                self.inter_line_counter = len(self.refPt)
                
                self.open_update_pairs_window()
                self.draw()
                    
        else:
            messagebox.showinfo("No image selected", "Please select an image first!")
                       
    def save_pairs(self):

        if self.image is not None:

            options = {}
            options['filetypes'] = [('Text file', '.txt'),
                                    ('Comma separated', '.csv'), ('All files', '*')]
            options['defaultextension'] = "txt"
            options['title'] = "Choose pairs file"

            filenames = asksaveasfilename(**options)

            if filenames:
                with open(filenames, 'w') as csv_file:

                    csv_writer = csv.writer(csv_file, delimiter=',')
                    csv_writer.writerow(self.refPt)                    
        else:
            messagebox.showinfo("No image selected", "Please select an image first!")
        
    def save_tracks(tracks_by_files_transformed):
        
        tracks_by_files_transformed
        
        try:
            for (filename, rows) in tracks_by_files_transformed:
            
                idx = len(filename) - 4
                res_filename = filename[:idx] + '_transformed' + filename[idx:]
                
                with open(res_filename, 'w') as txtfile:
                    wr = csv.writer(txtfile, lineterminator='\n')
                    
                    for row in rows:
                            
                        wr.writerow(row)
                    
        except Exception:

            e = sys.exc_info()[0]
            messagebox.showinfo("Error saving tracking boxes", e)
            raise
    
    def draw(self):        
        
        image = self.image.copy()
        
        x = 0
        x2 = 0
        while x < self.inter_line_counter - 1:
            image = self.put_points_and_line_on_image(image,
                        self.refPt[x], self.refPt[x + 1], x2)
            x += 2
            x2 += 1
        
        w = int(round(self.ref_image.shape[1] * (self.scale_width / 100), 0))
        ref_image = imutils.resize(self.ref_image, w)
        ref_image = imutils.rotate(ref_image, angle=int(self.rotate_grade))                    
        image = App.overlay_transparent(image, ref_image, 
                                        self.move_x - int(ref_image.shape[1] / 2), 
                                        self.move_y - int(ref_image.shape[0] / 2), 
                                        alpha=self.alpha)
        cv2.imshow("image", image)
        
    def draw_all_tracks(self):

        #should use self.draw_tracks and an additional load_tracks function. 
        if self.path_to_tracking_res:

            for i in range(0, len(self.path_to_tracking_res)):

                track_buffer_dict = {}
                rows = []

                with open(self.path_to_tracking_res[i], 'r') as csv_file:

                    csv_reader = csv.reader(csv_file, delimiter=',')
                    image = self.image.copy()

                    try:

                        for row in csv_reader:

                            rows.append(row)
                            track_id = int(row[1])                            
                            #track_class = int(float(row[7]))
                            
                            track_color = App.create_unique_color_int(track_id)
                            cy = (float(row[3]) + float(row[5])) * self.scale_factor
                            cx = (float(row[2]) + (float(row[4]) / 2)) * self.scale_factor
                            center = (int(cx), int(cy))

                            if track_id not in track_buffer_dict:
                                pts = deque([], maxlen=None)
                            else:
                                pts = track_buffer_dict[track_id]

                            if pts:
                                last_center = pts[-1]
                            else:
                                pts.append(center)
                                track_buffer_dict[track_id] = pts
                                continue

                            cv2.line(image, last_center, center, track_color, 1)

                            pts.append(center)
                            track_buffer_dict[track_id] = pts
                            
                        self.tracks_by_files.append((str(self.path_to_tracking_res[i]), rows.copy()))

                    except Exception:

                        e = sys.exc_info()[0]
                        messagebox.showinfo("Error parsing tracking file", e)
                        raise

            cv2.imshow('image', image)

        else:
            messagebox.showinfo("No tracking file chosen", "Please select an tracking file first!")

    def draw_tracks(self, image, tracks_by_files_transformed):
        
        w = int(round(self.ref_image.shape[1] * (self.scale_width / 100), 0))
        ref_image = imutils.resize(self.ref_image, w)
        ref_image = imutils.rotate(ref_image, angle=int(self.rotate_grade))
        image = App.overlay_transparent(image, ref_image, 
                                        self.move_x - int(ref_image.shape[1] / 2), 
                                        self.move_y - int(ref_image.shape[0] / 2), 
                                        alpha=0.1)
        
        for (filename, rows) in tracks_by_files_transformed:  

            track_buffer_dict = {}

            for row in rows:          

                    track_id = int(row[1])                            
                    #track_class = int(float(row[7]))
                    
                    track_color = App.create_unique_color_int(track_id)
                    cy = (float(row[3]) + float(row[5])) * self.scale_factor
                    cx = (float(row[2]) + (float(row[4]) / 2)) * self.scale_factor
                    center = (int(cx), int(cy))

                    if track_id not in track_buffer_dict:
                        pts = deque([], maxlen=None)
                    else:
                        pts = track_buffer_dict[track_id]

                    if pts:
                        last_center = pts[-1]
                    else:
                        pts.append(center)
                        track_buffer_dict[track_id] = pts
                        continue

                    cv2.line(image, last_center, center, track_color, 1)

                    pts.append(center)
                    track_buffer_dict[track_id] = pts
                    
            #self.tracks_by_files.append((str(filename), rows.copy()))

        cv2.imshow('image', image)

    def overlay_transparent(background_img, img_to_overlay_t, x, y, overlay_size=None, alpha=0.1):
        
        output = background_img.copy()
        overlay = background_img.copy()
                
        ho, wo, _ = output.shape
        h, w, _ = img_to_overlay_t.shape  
        
        x3 = 0
        y3 = 0         
        x2 = w + x
        y2 = y + h
        
        if x2 >= wo:
            x2 = wo
            w = wo - x
        
        if x < 0:                       
            x3 = -x
            x = 0 
        
        if y2 >= ho:
            y2 = ho
            h = ho - y
            
        if y < 0:            
            y3 = -y
            y = 0   
                
        output[y:y2, x:x2] = img_to_overlay_t[y3:h, x3:w]
        output = cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)
            
        return output
    
    def ask_for_ref_coordinates(self):

        window = Toplevel(self.root)
        window.wm_title("Enter ref coordinates")
        window.resizable(width=False, height=False)
        window.geometry('{}x{}'.format(250, 300))
        window.attributes('-topmost', True)
        
        label1 = Label(window, text="lat \n (top left corner of rectangle)")
        label1.pack(side="top", padx="10", pady="5")
        e2 = Entry(window)
        e2.config(width=10)
        e2.insert(END, self.lat_top_left)
        e2.pack(side="top", padx="10", pady="5")
        
        label2 = Label(window, text="long \n (top left corner of rectangle)")
        label2.pack(side="top", padx="10", pady="5")
        e3 = Entry(window)
        e3.config(width=10)
        e3.insert(END, self.long_top_left)
        e3.pack(side="top", padx="10", pady="5")
        
        label3 = Label(window, text="lat \n (bottom right corner of rectangle)")
        label3.pack(side="top", padx="10", pady="5")
        e4 = Entry(window)
        e4.config(width=10)
        e4.insert(END, self.lat_bottom_right)
        e4.pack(side="top", padx="10", pady="5")
        
        label4 = Label(window, text="long \n (bottom right corner of rectangle)")
        label4.pack(side="top", padx="10", pady="5")
        e5 = Entry(window)
        e5.config(width=10)
        e5.insert(END, self.long_bottom_right)
        e5.pack(side="top", padx="10", pady="5")
        
        btn1 = Button(window, text="Set", command=lambda *args: self.set_reference_coordinates(e2.get(), e3.get(), e4.get(), e5.get(), window))
        btn1.pack(side="top", fill="both", expand="yes", padx="10", pady="5")
        
        self.root.wait_window(window)
    
    def set_reference_coordinates(self, lat_top_left, long_top_left, lat_bottom_right, long_bottom_right, window):
        
        self.lat_top_left = lat_top_left
        self.long_top_left = long_top_left
        self.lat_bottom_right = lat_bottom_right
        self.long_bottom_right = long_bottom_right
            
        window.destroy()
        
    def get_line_mid_point(point1, point2):

        return ((point1[0] + point2[0]) / 2, (point1[1] + point2[1]) / 2)
    
    def create_unique_color_int(tag, hue_step=0.41):

        h, v, = (tag * hue_step) % 1, 1. - (int(tag * hue_step) % 4) / 5.
        r, g, b = colorsys.hsv_to_rgb(h, 1., v)

        return int(255 * r), int(255 * g), int(255 * b)
     
    def on_trackbar_alpha(self, val):
        
        self.alpha = round((val / 100), 1)
        self.draw()
    
    def on_trackbar_size(self, val):
        
        self.scale_width = val
        self.draw()
        
    def on_trackbar_rotate(self, val):
        
        self.rotate_grade = val
        self.draw()
    
    def on_trackbar_move_x(self, val):
        
        self.move_x = val
        self.draw()
    
    def on_trackbar_move_y(self, val):
        
        self.move_y = val
        self.draw()
        
    def on_closing():

        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            sys.exit()

if __name__ == '__main__':
    #    import sys

    App().run()
