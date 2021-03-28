from PIL import Image
import imagehash
import cv2


class ImageCompare(object):
    def aHash_compare(self, src_image, dst_image):
        """基于均值哈希算法比较图片

        Args:
            src_image (path): 源图片路径
            dst_image (path): 目标图片路径

        Returns:
            double: 相似度
        """
        image1 = Image.open(src_image)
        image2 = Image.open(dst_image)
        hash1 = imagehash.average_hash(image1)
        hash2 = imagehash.average_hash(image2)
        return (1 - (hash1 - hash2) / len(hash1.hash) ** 2)*100

    def dHash_compare(self, src_image, dst_image):
        """基于差值哈希算法比较图片

        Args:
            src_image (path): 源图片路径
            dst_image (path): 目标图片路径

        Returns:
            double: 相似度
        """
        image1 = Image.open(src_image)
        image2 = Image.open(dst_image)
        hash1 = imagehash.dhash(image1)
        hash2 = imagehash.dhash(image2)
        return (1 - (hash1 - hash2) / len(hash1.hash) ** 2)*100

    def pHash_compare(self, src_image, dst_image):
        """基于感知哈希算法比较图片

        Args:
            src_image (path): 源图片路径
            dst_image (path): 目标图片路径

        Returns:
            double: 相似度
        """
        image1 = Image.open(src_image)
        image2 = Image.open(dst_image)
        hash1 = imagehash.dhash(image1)
        hash2 = imagehash.dhash(image2)
        return (1 - (hash1 - hash2) / len(hash1.hash) ** 2)*100

    def _calculate(self, image1, image2):
        # 灰度直方图算法
        # 计算单通道的直方图的相似值
        hist1 = cv2.calcHist([image1], [0], None, [256], [0.0, 255.0])
        hist2 = cv2.calcHist([image2], [0], None, [256], [0.0, 255.0])
        # 计算直方图的重合度
        degree = 0
        for i in range(len(hist1)):
            if hist1[i] != hist2[i]:
                degree = degree + \
                    (1 - abs(hist1[i] - hist2[i]) / max(hist1[i], hist2[i]))
            else:
                degree = degree + 1
        degree = degree / len(hist1)
        return degree

    def classify_hist_with_split(self, image1, image2, size=(256, 256)):
        """直方图算法比较图片

        Args:
            image1 (path): 源图片路径
            image2 (path): 目标图片路径
            size (tuple, optional): 图片缩放尺寸. Defaults to (256, 256).

        Returns:
            double: 相似度
        """
        # RGB每个通道的直方图相似度
        # 将图像resize后，分离为RGB三个通道，再计算每个通道的相似值
        image1 = cv2.imread(image1)
        image2 = cv2.imread(image2)
        image1 = cv2.resize(image1, size)
        image2 = cv2.resize(image2, size)
        sub_image1 = cv2.split(image1)
        sub_image2 = cv2.split(image2)
        sub_data = 0
        for im1, im2 in zip(sub_image1, sub_image2):
            sub_data += self._calculate(im1, im2)
        sub_data = sub_data / 3
        return sub_data[0]*100
