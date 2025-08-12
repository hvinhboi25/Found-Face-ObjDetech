from ultralytics import YOLO
import torch
model = YOLO('yolov8n.pt')
#train bang gpu voi data.yaml 


if __name__ == '__main__':
    model.train(data='data.yaml', epochs=50, device='0')
