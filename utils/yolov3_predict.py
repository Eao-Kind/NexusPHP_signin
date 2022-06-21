from yolov3.yolov3_utils import *

device = torch.device("cpu")
output_folder = './'
conf_thres = 0.7
nms_thres = 0.4
model_def = "./yolov3/yolov3-captcha.cfg"
weights_path = "./yolov3/yolov3_ckpt_49.pth"
img_size = 416
img_path = "./yolov3/img1.png"
class_path = "./yolov3/classes.names"


def predict(image):
    """
    返回偏移量
    :param image: Open后的图片
    :return: 偏移量
    """
    model = Darknet(model_def, img_size=img_size).to(device)
    model.load_state_dict(torch.load(weights_path, map_location="cpu"))
    model.eval()  # Set in evaluation mode
    classes = load_classes(class_path)  # Extracts class labels from file
    Tensor = torch.FloatTensor
    img = transforms.ToTensor()(image.convert('RGB'))
    img, _ = pad_to_square(img, 0)
    img = resize(img, img_size)
    input_imgs = Variable(img.type(Tensor))
    input_imgs = img.unsqueeze(0)  # dataloader后会多一维，因此增加一维，输出的img格式为[1,C,H,W]
    input_imgs = Variable(input_imgs.type(Tensor))
    with torch.no_grad():
        detections = model(input_imgs)
        detections = non_max_suppression(detections, conf_thres, nms_thres)

    cmap = plt.get_cmap("tab20b")
    colors = [cmap(i) for i in np.linspace(0, 1, 20)]
    img = np.array(Image.open(img_path))
    plt.figure()
    fig, ax = plt.subplots(1)
    ax.imshow(img)
    if detections is not None:
        # Rescale boxes to original image
        detections = rescale_boxes(detections[0], img_size, img.shape[:2])  # 只有一个图片，detections[0]取第一个
        unique_labels = detections[:, -1].cpu().unique()
        n_cls_preds = len(unique_labels)
        bbox_colors = random.sample(colors, n_cls_preds)
        for x1, y1, x2, y2, conf, cls_conf, cls_pred in detections:
            print("\t+ Label: %s, Conf: %.5f" % (classes[int(cls_pred)], cls_conf.item()))

            box_w = x2 - x1
            box_h = y2 - y1
            color = bbox_colors[int(np.where(unique_labels == int(cls_pred))[0])]
            # Create a Rectangle patch
            # bbox = patches.Rectangle((x1 + box_w / 2, y1 + box_h / 2), box_w, box_h, linewidth=2, edgecolor=color, facecolor="none")
            # 这里和原作者代码有点区别，右下偏离了一半
            bbox = patches.Rectangle((x1, y1), box_w, box_h, linewidth=2, edgecolor=color, facecolor="none")
            print('bbox', (x1, y1, box_w, box_h), 'offset', x1)
            # Add the bbox to the plot
            ax.add_patch(bbox)
            # Add label
            plt.text(
                x1,
                y1,
                s=classes[int(cls_pred)],
                color="white",
                verticalalignment="top",
                bbox={"color": color, "pad": 0},
            )
            # only one
            break
    # Save generated image with detections
    plt.axis("off")
    plt.gca().xaxis.set_major_locator(NullLocator())
    plt.gca().yaxis.set_major_locator(NullLocator())
    plt.savefig("./yolov3/img1_1.png", bbox_inches="tight", pad_inches=0.0)
    plt.close()
    return x1.item()  # tensor转换为int


if __name__ == '__main__':
    image = Image.open('./yolov3/img1.png')
    print(predict(image))
