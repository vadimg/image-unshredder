import sys
from PIL import Image

def unshred(filename):
    image = Image.open(filename)

    width, height = image.size

    img = Img(image)

    # calculate distances between all adjacent vertical lines
    distances = []
    for i in xrange(width-1):
        distances.append(img.line_distance(i, i+1))

    # break the lines up into intervals and score them
    scores = []
    for i in xrange(2, width/2+1):
        if width % i == 0:
            scores.append((i, interval_score(distances, i)))

    # strip width is the interval with the highest score
    strip_width = max(scores, key=lambda x: x[1])[0]

    num_strips = width/strip_width

    # create a matrix of strip distances
    distances = [[None]*num_strips for _ in xrange(num_strips)]
    for p1 in xrange(num_strips):
        for p2 in xrange(num_strips):
            distances[p1][p2] = img.strip_distance(strip_width, p1, p2)

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

# euclidean distance between 2 n-dimensional points
def distance(p1, p2):
    return sum((a-b)**2 for a, b in zip(p1, p2))**(.5)

# returns number not found in list of numbers between 0 and len(l)
def hole(l):
    for n in xrange(len(l)):
        if n not in l:
            return n

def mean(l):
    return sum(l)/len(l)

# assigns a score to an interval based on a proprietary algorithm ;)
def interval_score(l, interval):
    ints = []
    for i in xrange(interval-1, len(l), interval):
        ints.append(l[i])

    ex = set(l) - set(ints)

    return mean(ints) - max(ex)

class Img(object):
    def __init__(self, image):
        self._image = image
        self._pixels = image.getdata()

    def get_pixel(self, x, y):
        width, height = self._image.size
        pixel = self._pixels[y * width + x]
        return pixel

    # sum of all euclidean distances between the
    # right part of strip n1 and the left part of strip n2
    def strip_distance(self, strip_width, n1, n2):
        x1 = n1 * strip_width + (strip_width-1)
        x2 = n2 * strip_width
        return self.line_distance(x1, x2)

    # sum of all euclidean distances between 2 vertical lines
    def line_distance(self, x1, x2):
        s = 0
        for y in xrange(self._image.size[1]):
            p1 = self.get_pixel(x1, y)
            p2 = self.get_pixel(x2, y)
            s += distance(p1, p2)
        return s

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

