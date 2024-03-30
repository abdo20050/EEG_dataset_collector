import tkinter as tk
from PIL import Image, ImageTk 
from label_generate import generate_labels
import time
import atexit
import os
import glob

def read_png_names(directory):
    labels = []
    # Use glob to match the pattern '*.png'
    files = glob.glob(os.path.join(directory, '*.png'))
    for file in files:
        labels.append(os.path.basename(file).replace('.png',''))
    return labels

recorder = None
# labels = ['break','forward','backward', 'left', 'right']  # Labels for the markers
def display_image(images_path, label_generator , image_duration = 4000, break_duration = 1000, recorder = recorder, labels = ['break','forward','backward', 'left', 'right']):
    #non local variables
    break_time = True
    curLabel = "break"
    nextLabel = label_generator()
    record_dic={i:0 for i in labels}
    root = tk.Tk()
    def on_closing():
        sum = 0
        for i in record_dic:
            sum += record_dic[i]
        print(sum)
        if(recorder != None):
            print(recorder.exportedSum)
        root.destroy()
        if recorder != None:
            # print('bye')
            recorder.exit_fun()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    remaining_time_label = tk.Label(root, text="Remaining Time: {} ms".format(break_duration/1000))
    remaining_time_label.pack(side="top", pady=10)
    motion_label_label = tk.Label(root, text="Current label is: {}".format(curLabel))
    motion_label_label.pack(side="top", pady=10)
    Images = { i : Image.open(images_path+(i+".png")).convert("RGBA") for i in labels}
    print(Images)
    breakImg = Images[nextLabel]
    white_layer = Image.new('RGBA', breakImg.size,color=(255,255,255,255))
    transparent_layer = Image.new('RGBA', breakImg.size,color=(255,255,255,0))
    photo = ImageTk.PhotoImage(breakImg)
    panel = tk.Label(root, image=photo)
    panel.pack(side="bottom", fill="both", expand="yes")
    interval = 100
    prev_time = time.time()
    root.title("Image Display")
            # recorder.visThread.join()
    def show_next_image(image ,remaining_time):
        nonlocal break_time
        nonlocal curLabel
        nonlocal nextLabel
        nonlocal interval
        nonlocal prev_time
        if not break_time :
            remaining_time_label.config(text="Remaining Time: {} ms".format(round(remaining_time/1000,1)))
        else: 
            remaining_time_label.config(text="Remaining Time: 0.0 ms")
        motion_label_label.config(text="Current label is: {}".format(curLabel.replace( '_',' ')))
        curImg = image
        
        if remaining_time > 0:
            
            if 1:
                duration = break_duration if break_time else image_duration
                transition_interval = 500
                startAlphaFactor = max(0,(duration - remaining_time-100)/transition_interval)
                endAlphaFactor = float(remaining_time)/transition_interval
                betweenAlphaFactor = min(1,max(0,(duration - remaining_time - transition_interval-200)/transition_interval))
                bgImg = curImg.copy()
                if break_time:
                    if startAlphaFactor < 1:
                        bgImg = Image.blend(bgImg,white_layer,alpha=startAlphaFactor)
                        fgImg = Image.blend(transparent_layer,Images["break"],alpha=min(1,startAlphaFactor)*0.5)
                        new_img = Image.alpha_composite(bgImg,fgImg)
                    elif startAlphaFactor >= 1 and endAlphaFactor >1:
                        curImg = Images[nextLabel]
                        bgImg = curImg.copy()
                        bgImg = Image.blend(bgImg,transparent_layer,alpha= 1 - betweenAlphaFactor)
                        fgImg = Image.blend(Images["break"],transparent_layer,alpha=0.5)
                        new_img = Image.alpha_composite(bgImg,fgImg)
                    elif endAlphaFactor <= 1 and recorder != None and recorder.isDoneExport == False:#wait till export is done
                        remaining_time += 200
                        curImg = Images[nextLabel]
                        bgImg = curImg.copy()
                        bgImg = Image.blend(bgImg,transparent_layer,alpha= 1 - betweenAlphaFactor)
                        fgImg = Image.blend(Images["break"],transparent_layer,alpha=0.5)
                        new_img = Image.alpha_composite(bgImg,fgImg)
                    elif endAlphaFactor <= 1:
                        
                        curImg = Images[nextLabel]
                        bgImg = curImg.copy()
                        fgImg = Image.blend(transparent_layer,Images['break'] ,alpha=endAlphaFactor*0.5)
                        new_img = Image.alpha_composite(bgImg,fgImg)
                    new_img = Image.alpha_composite(bgImg,fgImg)
                else: 
                    new_img = Images[nextLabel]
                # new_img = Images[nextLabel]
                # print(nextLabel)
                photo = ImageTk.PhotoImage(new_img)
                panel.configure(image=photo)
                panel.image = photo
            root.update()
            real_interval = round((time.time()-prev_time)*1000 , 3)
            prev_time = time.time()
            # print(real_interval)
            remaining_time = max(remaining_time - real_interval,0)
            root.after(interval, lambda: show_next_image(curImg, remaining_time))
        else:
            break_time = not break_time
            if break_time:
                if recorder != None:
                    recorder.stop_record()
                    pass
                    # recorder.export_record(recorder.record_export_folder, recorder.record_export_data_types,
                        #    recorder.record_export_format, [recorder.record_id], recorder.record_export_version)
                record_dic[curLabel] += 1 
                curLabel = "break"
                nextLabel = label_generator()
            else :
                curLabel = nextLabel
                if recorder != None:
                    # time.sleep(0.5)
                    recorder.record_export_folder = "D:/grad_proj/dataset_collect_script/records/"+curLabel
                    recorder.record_title = curLabel[0:2]+recorder.record_title[2:]
                    recorder.create_record(recorder.record_title)
                
        
            duration = break_duration if break_time else image_duration
            # print(duration)
            interval = 10 if break_time else 100
            root.after(interval, lambda: show_next_image(curImg, duration))  # Reset timer for next image
    root.after(interval, show_next_image(breakImg ,break_duration))  # Start the image display loop
    # root.protocol("WM_DELETE_WINDOW", on_closing(markerObj))

    root.mainloop()
def main(img_path, duration,recorder = None):
    images_path = img_path
    image_duration = duration  # Display each image for 4000 milliseconds (5 seconds)
    break_duration = 2000
    imgs_labels = read_png_names(images_path)
    labels_to_gen = [i for i in imgs_labels]
    # labels_to_gen.remove('break')
    print(labels_to_gen)
    label_generator = generate_labels(1000, labels_to_gen)
    display_image(images_path, label_generator ,image_duration = image_duration, break_duration = break_duration,labels = imgs_labels,recorder = recorder)


# Example usage:
if __name__ == "__main__":

    # Please fill your application clientId and clientSecret before running script
    your_app_client_secret = 'vPH10CLp9USN7DDQxx6ZBLPstEd8lq0VxzEgXGX8EWglje5ZF3uJPlF9XzRWxzKsuurKvFC6jQEhOTHc0RKU2wyfJE56xBWRxc5bnoMHIhX7FquWotsm1U3t2glQNDWT'
    your_app_client_id = 'uJvc5Kx0cft1pkPGwzQJ2ju2g3Q9gOpdFuWtYTNS'

    # atexit.register(exit_handler(m))
    images_path = "./_images/"
    image_duration = 4000  # Display each image for 5000 milliseconds (5 seconds)
    break_duration = 2000
    imgs_labels = read_png_names(images_path)
    labels_to_gen = [i for i in imgs_labels]
    # labels_to_gen.remove('break')
    print(labels_to_gen)
    label_generator = generate_labels(250, labels_to_gen)
    display_image(images_path, label_generator ,image_duration = image_duration, break_duration = break_duration,labels = imgs_labels)
