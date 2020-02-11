from PIL import Image
import torch
from torch.autograd import Variable
import torch.nn as nn
import torchvision.transforms as transforms
import numpy as np
from config import *


transforms = transforms.Compose([
        #transforms.Grayscale(), 
        transforms.ToTensor(),  
        #transforms.Normalize(mean=[0.5], std=[0.5])
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])


class VGG(nn.Module):
    def __init__(self):
        super(VGG, self).__init__()
        self.features = self._make_layers([64, 64, 'M', 128, 128, 'M', 256, 256, 256, 'M', 512, 512, 512, 'M', 512, 512, 512, 'M'])
        self.classifier = nn.Sequential(
            nn.Linear(9216, MAX_CAPTCHA*ALL_CHAR_SET_LEN)
        )

    def forward(self, x):
        out = self.features(x)
        out = out.view(out.size(0), -1)
        out = self.classifier(out)
        return out

    def _make_layers(self, cfg):
        layers = []
        in_channels = 3
        for x in cfg:
            if x == 'M':

                layers += [nn.MaxPool2d(kernel_size=2, stride=2, padding=1)]
            else:
                layers += [nn.Conv2d(in_channels, x, kernel_size=3, padding=1),
                           nn.BatchNorm2d(x),
                           nn.ReLU(inplace=True)]
                in_channels = x
        layers += [nn.AvgPool2d(kernel_size=1, stride=1)]
        return nn.Sequential(*layers)


def predict(image):
    my_cnn = VGG() 
    if torch.cuda.is_available():
        my_cnn.cuda()
    my_cnn.load_state_dict(torch.load('16pt.pth'))  
    image = transforms(image)  # 这里经过转换后输出的input格式是[C,H,W],网络输入还需要增加一维批量大小B
    image = image.unsqueeze(0)  # 增加一维，输出的img格式为[1,C,H,W]
    vimage = Variable(image).cuda()  
    predict_label = my_cnn(vimage)
    c0 = ALL_CHAR_SET[np.argmax(predict_label[0, 0:  ALL_CHAR_SET_LEN].data.cpu().numpy())]
    c1 = ALL_CHAR_SET[np.argmax(predict_label[0, 1 * ALL_CHAR_SET_LEN:2 * ALL_CHAR_SET_LEN].data.cpu().numpy())]
    c2 = ALL_CHAR_SET[np.argmax(predict_label[0, 2 * ALL_CHAR_SET_LEN:3 * ALL_CHAR_SET_LEN].data.cpu().numpy())]
    c3 = ALL_CHAR_SET[np.argmax(predict_label[0, 3 * ALL_CHAR_SET_LEN:4 * ALL_CHAR_SET_LEN].data.cpu().numpy())]
    c4 = ALL_CHAR_SET[np.argmax(predict_label[0, 4 * ALL_CHAR_SET_LEN:5 * ALL_CHAR_SET_LEN].data.cpu().numpy())]
    c5 = ALL_CHAR_SET[np.argmax(predict_label[0, 5 * ALL_CHAR_SET_LEN:6 * ALL_CHAR_SET_LEN].data.cpu().numpy())]
    predict_label = '%s%s%s%s%s%s' % (c0, c1, c2, c3, c4, c5)
    return predict_label


if __name__ == '__main__':
    img = Image.open('temp.png')
    print(predict(img))
