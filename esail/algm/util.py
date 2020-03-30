from math import cos, asin, sqrt,degrees,acos,ceil,floor
import matplotlib.pyplot as plt
from haversine import haversine


def get_colors() :
    color_list = ['yellow','blue','red','green','cyan']
    return color_list

def is_divide_pt(x11,y11, x12,y12, x21,y21, x22,y22):
    f1 = (x12 - x11) * (y21 - y11) - (y12 - y11) * (x21 - x11)
    f2 = (x12 - x11) * (y22 - y11) - (y12 - y11) * (x22 - x11)
    if f1 * f2 <= 0:
        return True
    else:
        return False



def is_cross_pt(x11,y11, x12,y12, x21,y21, x22,y22):
    b1 = is_divide_pt(x11,y11, x12,y12, x21,y21, x22,y22)
    b2 = is_divide_pt(x21,y21, x22,y22, x11,y11, x12,y12)
    if b1 and b2:
        return True


    """
    직선 방정식 교점을 구한다.
    :param p1,p2 : 직선방정식 좌표 
    :param p3,p4 : 직선방정식 좌표
    :return:         
    """
def get_cross_point(p1, p2, p3, p4):
    # print(self.calc_distance(start,dest))
    x11 = p1[1]
    y11 = p1[0]
    x12 = p2[1]
    y12 = p2[0]

    x21 = p3[1]
    y21 = p3[0]
    x22 = p4[1]
    y22 = p4[0]

    if x12 == x11 or x22 == x21:
        #print('delta x=0')
        if x12 == x11:
            if (x22 == x21):
                "네점의  x좌표가 동일 (181,181)"
                return None
            cx = x12
            m2 = (y22 - y21) / (x22 - x21)
            cy = m2 * (cx - x21) + y21
            if is_cross_pt(x11, y11, x12, y12, x21, y21, x22, y22):
                return (round(cy, 7), round(cx, 7))
            else:
                return None
        if x22 == x21:
            if (x12 == x11):
                "네점의  x좌표가 동일(181,181)"
                return None
            cx = x22
            m1 = (y12 - y11) / (x12 - x11)
            cy = m1 * (cx - x11) + y11
            if is_cross_pt(x11, y11, x12, y12, x21, y21, x22, y22):
                return (round(cy, 7), round(cx, 7))
            else:
                return None

    m1 = (y12 - y11) / (x12 - x11)
    m2 = (y22 - y21) / (x22 - x21)
    if m1 == m2:
        "평행(182,182)"
        #print('평행')
        return None
    # print(x11, y11, x12, y12, x21, y21, x22, y22, m1, m2)
    cx = round((x11 * m1 - y11 - x21 * m2 + y21) / (m1 - m2),7)
    cy = round(m1 * (cx - x11) + y11,7)

    #util.display_coord(x11, x12,x21,x22,y11, y12,y21,y22)
    "구한 교점이 범위내에 있는치 체크"
    if is_cross_pt(x11,y11, x12,y12, x21,y21, x22,y22):
        return (round(cy,7), round(cx,7))
    else:
        #print("No 교점 ======> ",p1, p2, p3, p4)
        return None



def calc_distance(start, dest):
    """
    주어진 좌표간 거리를 구한다.(km)
    :param start(위도,경도
    :param end(위도,경도)
    :return:
    """
    lat1 = start[0]
    lat2 = dest[0]

    lon1 = start[1]
    lon2 = dest[1]

    p = 0.017453292519943295  # Pi/180
    a = 0.5 - cos((lat2 - lat1) * p) / 2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    return 12742 * asin(sqrt(a))  # 2*R*asin...


# 거리 구하기
def calc_haversine(start,dest,unit):
    if(unit == 'km') :
        return haversine(start,dest)
    else :
        return haversine(start,dest,unit)


def display_coord(x11,y11, x12,y12, x21,y21, x22,y22):
    #plt.plot([start_long, dest_long], [start_lat, dest_lat], c=r)
    plt.plot([x11, x12], [y11, y12], c='r')
    plt.plot([x21, x22], [y21, y22], c='b')
    plt.show()




"구한 좌표가 선분범위에 있는지 체크"
def check_x_range(x11,x12,cx) :
    if((cx >= min(x11,x12) and cx <= max(x11,x12))):
        return True
    else :
        return False



"벡터 내적이용해서 장애물이 경로(선분의 수직인 곳에 있는지 체크"
def check_range(point,start,dest) :
    x01 = float(point[1])
    y01 = float(point[0])

    x11 = start[1]
    y11 = start[0]
    x12 = dest[1]
    y12 = dest[0]

    a_vector = (x01 - x11, y01 - y11)
    b_vector = (x12 - x11, y12 - y11)
    
    #벡터 내적
    inner_value = a_vector[0]*b_vector[0] + a_vector[1]*b_vector[1]
    b_vector_scalar = dist_vector(b_vector)
    
    # 두벡터 크기 곱

    scalar_product = dist_vector(a_vector) *  dist_vector(b_vector)

    # 선분의 꼭지점에 장애물이 있으면 True
    if scalar_product == 0.0 :
        return True
    # 코사인 값
    cos_value = inner_value/ scalar_product
 
    # 정사영값
    projectction_value_a = dist_vector(a_vector) * cos_value      # 정사영값

    # 벡터a 의 정상영값이 벡터 b (선분)의 길이보다 크면 선분 범위 벗어 남 작으면 선분내에 있음
    if(projectction_value_a >= 0 and projectction_value_a <= b_vector_scalar) :
        return True

def dist_vector(v):
    scalar = sqrt(v[0]**2+v[1]**2)
    return scalar




# 점과 선분 사이의 거리
def dist_point_to_line(point,start,dest):
    #print("포인트 = ",point)
    x01 = float(point[1])
    y01 = float(point[0])

    x11 = start[1]
    y11 = start[0]
    x12 = dest[1]
    y12 = dest[0]
    #is_inner = check_range(x11,x12,x01)
    is_inner = check_range(point,start,dest)
    if(is_inner) : # 선분 내부에 있고 넓이가 0 이면 거리는 0 
        area = abs((x11 - x01) * (y12 - y01) - (y11 - y01) * (x12 - x01))
        if(area == 0) :
            return 0.0
        else :
            line_length = ((x11 - x12) ** 2 + (y11 - y12) ** 2) ** 0.5
            dis = round((area / line_length), 7)
            return dis
    else :   # 선분 내부에 없으면 선분의 양 꼭지점에서 짧은 거리를 선택
        dis_01 = ((x01 - x11) ** 2 + (y01 - y11) ** 2) ** 0.5
        dis_02 = ((x01 - x12) ** 2 + (y01 - y12) ** 2) ** 0.5
        dis = min(dis_01, dis_02)
        #print("장애물 간 거리 ================================================>", dis)
        return dis



"선분과 장애물사이의 거리"
def distance_barriers(barriers,start,end):
    for barrier in barriers:
        for bar in barrier:
            distance = dist_point_to_line(bar, start, end)
            #print("직선사이 거리 ===== >", bar, start, end, distance)
            if distance < 0.5 :
                return distance
    return 1000



"격자 간격을 맞추기 이해 좌표값에 따라 올림 또는 반올림 "
def get_rounding(start,dest):
    x11 = start[1]
    y11 = start[0]
    x12 = dest[1]
    y12 = dest[0]

    dx = x12 - x11
    dy = y12 - y11
    filter_value = 10  # 소숫점 처리
    if dx > 0 :
        x11 = ceil(x11*filter_value)/filter_value
        x12 = floor(x12*filter_value)/filter_value
    else :
        x11 = floor(x11 * filter_value) / filter_value
        x12 = ceil(x12 * filter_value) / filter_value

    if dy > 0:
        y11 = ceil(y11 * filter_value) / filter_value
        y12 = floor(y12 * filter_value) / filter_value
    else:
        y11 = floor(y11 * filter_value) / filter_value
        y12 = ceil(y12 * filter_value) / filter_value

    return (y11,x11), (y12,x12)


#print(dist_point_to_line((8,6) ,(5.0, 5.0) ,(7, 6)))
print(calc_distance((5.0, 5.0) ,(5, 6)))
print(haversine((5.0, 5.0) ,(5, 6)))
#print(get_rounding((34.5708333, 128.6463889),(34.4741667, 128.0738889)))


