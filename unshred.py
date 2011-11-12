import sys
from PIL import Image

STRIP_WIDTH = 32

# euclidean distance between 2 n-dimensional points
def distance(p1, p2):
    return sum((a-b)**2 for a, b in zip(p1, p2))**(.5)

# returns number not found in list of numbers between 0 and len(l)
def hole(l):
    for n in xrange(len(l)):
        if n not in l:
            return n

class Img(object):
    def __init__(self, image):
        self.image = image
        self._pixels = image.getdata()

    def get_pixel(self, x, y):
        width, height = self.image.size
        pixel = self._pixels[y * width + x]
        return pixel

    # sum of all euclidean distances between the
    # right part of strip n1 and the left part of strip n2
    def strip_distance(self, n1, n2):
        x1 = n1 * STRIP_WIDTH + (STRIP_WIDTH-1)
        x2 = n2 * STRIP_WIDTH
        return self.line_distance(x1, x2)

    # sum of all euclidean distances between 2 vertical lines
    def line_distance(self, x1, x2):
        s = 0
        for y in xrange(self.image.size[1]):
            p1 = self.get_pixel(x1, y)
            p2 = self.get_pixel(x2, y)
            s += distance(p1, p2)
        return s

def unshred(filename):
    image = Image.open(filename)

    img = Img(image)

    width, height = image.size
    num_strips = width/STRIP_WIDTH

    # create a matrix of strip distances
    distances = [[None]*num_strips for _ in xrange(num_strips)]
    for p1 in xrange(num_strips):
        for p2 in xrange(num_strips):
            distances[p1][p2] = img.strip_distance(p1, p2)

    # nexts[i] = j means strip j comes right after strip i
    nexts = []
    for l in distances:
        nexts.append(l.index(min(l)))

    first = hole(nexts) # the first strip

    # build the rest of the strips in order
    inorder = [first]
    for _ in xrange(len(nexts)-1):
        inorder.append(nexts[inorder[-1]])

    builder = UnshredBuilder(image, num_strips)
    for i in inorder:
        builder.append(i)

    builder.save()

class UnshredBuilder(object):
    def __init__(self, shredded_image, ncols):
        self._shredded_image = shredded_image
        self._unshredded = Image.new('RGBA', shredded_image.size)
        self._shred_width = self._unshredded.size[0]/ncols
        self._height = self._shredded_image.size[1]
        self._n = 0

    # appends strip n from the shredded image to the unshredded image
    def append(self, n):
        x1, y1 = self._shred_width * n, 0
        x2, y2 = x1 + self._shred_width, self._height

        source_region = self._shredded_image.crop((x1, y1, x2, y2))
        destination_point = (self._n * self._shred_width, 0)

        self._unshredded.paste(source_region, destination_point)

        self._n += 1

    def save(self):
        self._unshredded.save('unshredded.jpg', 'JPEG')

if __name__ == '__main__':
    unshred(sys.argv[1])

