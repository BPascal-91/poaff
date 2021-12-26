#!/usr/bin/env python3

import requests
import math

def test1RequestsAPIwithURL() -> None:
    GOOGLE_MAPS_API_URL = "https://maps.googleapis.com/maps/api/geocode/json"
    #GOOGLE_MAPS_API_URL = "https://maps.googleapis.com/maps/api/js?key=AIzaSyB41DRUbKWJHPxaFjMAwdrzWzbVKartNGg&libraries=geometry"
    #GOOGLE_MAPS_API_URL = "https://maps.googleapis.com/maps/api/js?v=3&libraries=geometry"
    #GOOGLE_MAPS_API_URL = "https://maps.googleapis.com/maps/api/js?v=3"

    params = {
        'key': 'yourKey',
        'address': '221B Baker Street, London, United Kingdom',
        'sensor': 'false',
        'region': 'uk'
    }

    # Do the request and get the response data
    req = requests.get(GOOGLE_MAPS_API_URL, params=params)
    res = req.json()
    if "error_message" in res:
        print(res)
        return

    # Use the first result
    result = res['results'][0]

    geodata = dict()
    geodata['lat'] = result['geometry']['location']['lat']
    geodata['lng'] = result['geometry']['location']['lng']
    geodata['address'] = result['formatted_address']

    print('{address}. (lat, lng) = ({lat}, {lng})'.format(**geodata))
    # 221B Baker Street, London, Greater London NW1 6XE, UK. (lat, lng) = (51.5237038, -0.1585531)
    return

def test2RequestsAPIwithURL() -> None:
    import urllib.request, urllib.parse, urllib.error
    import json
    #import ssl

    #api_key = False
    # If you have a Google Places API key, enter it here
    api_key = 42
    # https://developers.google.com/maps/documentation/geocoding/intro

    serviceurl = 'http://py4e-data.dr-chuck.net/json?'

    #address = input('Enter location: ')
    address = "universidad complutense de madrid"

    parms = dict()
    parms['address'] = address
    if api_key is not False: parms['key'] = api_key
    url = serviceurl + urllib.parse.urlencode(parms)

    print('Retrieving', url)
    uh = urllib.request.urlopen(url)
    data = uh.read().decode()
    print('Retrieved', len(data), 'characters')

    info = json.loads(data)

    #print(json.dumps(info, indent=4))
    print(info['results'][0]['place_id'])

    #output
    #Enter location: universidad complutense de madrid
    #Retrieving http://py4e-data.dr-chuck.net/json?address=universidad+complutense+de+madrid&key=42
    #Retrieved 2088 characters
    #ChIJgwhILT8oQg0REXLUZnurSe0
    return

class geocoding:
    # Copyright (c) 2007 Wyatt Baldwin
    #
    # Permission is hereby granted, free of charge, to any person
    # obtaining a copy of this software and associated documentation
    # files (the "Software"), to deal in the Software without
    # restriction, including without limitation the rights to use,
    # copy, modify, merge, publish, distribute, sublicense, and/or sell
    # copies of the Software, and to permit persons to whom the
    # Software is furnished to do so, subject to the following
    # conditions:
    #
    # The above copyright notice and this permission notice shall be
    # included in all copies or substantial portions of the Software.
    #
    # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    # EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
    # OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    # NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
    # HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
    # WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    # FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
    # OTHER DEALINGS IN THE SOFTWARE.

    def __init__(self)-> None:
        self.num_levels = 4
        self.zoom_factor = 32
        return

    # Enter points array in geoJSON format [lon, lat]
    def encode(self, points, threshold=0.00001):
        """Encode a set of long/lat points.
        ``points``
            A list of long/lat points ((long, lat), ...)
            Note carefully that the order is longitude, latitude
        return
            - An encoded string representing points within our error
              ``threshold``,
            - An encoded string representing the maximum zoom level for each of
              those points
        Example::
            >>> pairs = ((-120.2, 38.5), (-126.453, 43.252), (-120.95, 40.7))
            >>> encode(pairs)
            '_p~iF~ps|U_c_\\\\fhde@~lqNwxq`@'
        """
        encoded_points = []
        #encoded_levels = []

        distances = self.douglas_peucker_distances(points, threshold)
        points_of_interest = []
        for i, d in enumerate(distances):
            if d is not None:
                long, lat = points[i]
                points_of_interest.append((lat, long, d))

        lat_prev, long_prev = 0, 0
        for lat, long, d in points_of_interest:
            encoded_lat, lat_prev = self.encode_lat_or_long(lat, lat_prev)
            encoded_long, long_prev = self.encode_lat_or_long(long, long_prev)
            encoded_points += [encoded_lat, encoded_long]
            #encoded_level = self.encode_unsigned(self.num_levels - self.compute_level(d) - 1)
            #encoded_levels.append(encoded_level)

        encoded_points_str = ''.join(encoded_points)
        #encoded_levels_str = ''.join([str(l) for l in encoded_levels])
        return encoded_points_str #, encoded_levels_str

    # Enter points array in format (lat, lon)
    def encode_pairs(self, points, threshold=0.00001):
        """Encode a set of lat/long points.
        ``points``
            A list of lat/long points ((lat, long), ...)
            Note carefully that the order is latitude, longitude
        return
            - An encoded string representing points within our error
              ``threshold``,
            - An encoded string representing the maximum zoom level for each of
              those points
        Example::
            >>> pairs = ((38.5, -120.2), (43.252, -126.453), (40.7, -120.95))
            >>> encode_pairs(pairs)
            ('_p~iF~ps|U_c_\\\\fhde@~lqNwxq`@', 'BBB')
        """
        encoded_points = []
        encoded_levels = []

        distances = self.douglas_peucker_distances(points, threshold)
        points_of_interest = []
        for i, d in enumerate(distances):
            if d is not None:
                lat, long = points[i]
                points_of_interest.append((lat, long, d))

        lat_prev, long_prev = 0, 0
        for lat, long, d in points_of_interest:
            encoded_lat, lat_prev = self.encode_lat_or_long(lat, lat_prev)
            encoded_long, long_prev = self.encode_lat_or_long(long, long_prev)
            encoded_points += [encoded_lat, encoded_long]
            encoded_level = self.encode_unsigned(self.num_levels - self.compute_level(d) - 1)
            encoded_levels.append(encoded_level)

        encoded_points_str = ''.join(encoded_points)
        encoded_levels_str = ''.join([str(l) for l in encoded_levels])
        return encoded_points_str, encoded_levels_str

    def encode_lat_or_long(self, x, prev_int):
        """Encode a single latitude or longitude.
        ``x``
            The latitude or longitude to encode

        ``prev_int``
            The integer value of the previous latitude or longitude

        Return the encoded value and its int value, which is used

        Example::
            >>> x = -179.9832104
            >>> encoded_x, prev = encode_lat_or_long(x, 0)
            >>> encoded_x
            '`~oia@'
            >>> prev
            -17998321
            >>> x = -120.2
            >>> encode_lat_or_long(x, prev)
            ('al{kJ', -12020000)
        """
        int_value = int(x * 1e5)
        delta = int_value - prev_int
        return self.encode_signed(delta), int_value

    def encode_signed(self, n):
        tmp = n << 1
        if n < 0:
            tmp = ~tmp
        return self.encode_unsigned(tmp)

    def encode_unsigned(self, n):
        tmp = []
        # while there are more than 5 bits left (that aren't all 0)...
        while n >= 32:  # 32 == 0xf0 == 100000
            tmp.append(n & 31)  # 31 == 0x1f == 11111
            n = n >> 5
        tmp = [(c | 0x20) for c in tmp]
        tmp.append(n)
        tmp = [(i + 63) for i in tmp]
        tmp = [chr(i) for i in tmp]
        tmp = ''.join(tmp)
        return tmp

    def douglas_peucker_distances(self, points, threshold=0.00001):
        distances = [None] * len(points)
        distances[0] = threshold * (self.zoom_factor ** self.num_levels)
        distances[-1] = distances[0]

        if(len(points) < 3):
            return distances

        stack = [(0, len(points) - 1)]
        while stack:
            a, b = stack.pop()
            max_dist = 0
            for i in range(a + 1, b):
                dist = self.distance(points[i], points[a], points[b])
                if dist > max_dist:
                    max_dist = dist
                    max_i = i
            if max_dist > threshold:
                distances[max_i] = max_dist
                stack += [(a, max_i), (max_i, b)]
        return distances

    def distance(self, point, A, B):
        """Compute distance of ``point`` from line ``A``, ``B``."""
        if A == B:
            out = math.sqrt(
                (B[0] - point[0]) ** 2 +
                (B[1] - point[1]) ** 2
            )
        else:
            u = (
                (((point[0] - A[0]) * (B[0] - A[0])) +
                 ((point[1] - A[1]) * (B[1] - A[1]))) /
                (((B[0] - A[0]) ** 2) +  ((B[1] - A[1]) ** 2))
            )
            if u <= 0:
                out = math.sqrt(
                    ((point[0] - A[0]) ** 2) + ((point[1] - A[1]) ** 2)
                )
            elif u >= 1:
                out = math.sqrt(
                    ((point[0] - B[0]) ** 2) + ((point[1] - B[1]) ** 2)
                )
            elif 0 < u < 1:
                out = math.sqrt(
                    ((((point[0] - A[0]) - (u * (B[0] - A[0]))) ** 2)) +
                    ((((point[1] - A[1]) - (u * (B[1] - A[1]))) ** 2))
                )
        return out

    def compute_level(self, distance, threshold=0.00001):
        """Compute the appropriate zoom level of a point in terms of its
        distance from the relevant segment in the DP algorithm."""
        zoom_level_breaks = self.compute_zoom_level_breaks(threshold)
        if distance > threshold:
            level = 0
        while distance < zoom_level_breaks[level]:
            level += 1
        return level

    def compute_zoom_level_breaks(self, threshold=0.00001):
        zoom_level_breaks = []
        for i in range(self.num_levels):
            zoom_level_breaks.append(threshold * (self.zoom_factor ** (self.num_levels - i - 1)))
        return zoom_level_breaks

    def test_encode_negative(self, ):
        f = -179.9832104
        assert self.encode_lat_or_long(f, 0)[0] == '`~oia@'

        f = -120.2
        assert self.encode_lat_or_long(f, 0)[0] == '~ps|U'

    def test_encode_positive(self, ):
        f = 38.5
        assert self.encode_lat_or_long(f, 0)[0] == '_p~iF'

    def test_encode_one_pair(self, ):
        pairs = [(38.5, -120.2)]
        expected_encoding = '_p~iF~ps|U', 'B'
        assert self.encode_pairs(pairs) == expected_encoding

    def test_encode_pairs(self, ):
        pairs = (
            (38.5, -120.2),
            (40.7, -120.95),
            (43.252, -126.453),
            (40.7, -120.95),
        )
        expected_encoding = '_p~iF~ps|U_ulLnnqC_mqNvxq`@~lqNwxq`@', 'BBBB'
        assert self.encode_pairs(pairs) == expected_encoding

        pairs = (
            (37.4419, -122.1419),
            (37.4519, -122.1519),
            (37.4619, -122.1819),
        )
        expected_encoding = 'yzocFzynhVq}@n}@o}@nzD', 'B@B'
        assert self.encode_pairs(pairs) == expected_encoding


if __name__ == '__main__':
    #test2RequestsAPIwithURL()
    #test2RequestsAPIwithURL()

    geoCod:geocoding = geocoding()

    # Enter points array in format (lat, lon)
    coords1 = ((49.516944, -0.000833),(49.625, 0.138333),(49.585556, 0.213056),(49.476667, 0.073333),(49.516944, -0.000833))
    pts1, lev1 = geoCod.encode_pairs(coords1)
    print (pts1)

    # Enter points array in geoJSON format [lon, lat]
    coords2 = [[-0.000833, 49.516944], [0.138333, 49.625], [0.213056, 49.585556], [0.073333, 49.476667], [-0.000833, 49.516944]]
    pts2 = geoCod.encode(coords2)
    print (pts2)
    assert pts1 == pts2


    """
    # ----------------------------------
    #Extract of poaff Openair file
    # ----------------------------------
    AC RMZ
    AN RMZ LE HAVRE (FFVL-Prot)
    *AUID GUId=LFSRMZOH UId=25090928 Id=LFSRMZOH
    *AAlt ["SFC/2500FT AMSL", "0m/762m"]
    *ADescr LE HAVRE AFIS SKED
    *AActiv (Pascal Bazile: Voir protocole https://federation.ffvl.fr/sites/ffvl.fr/files/Protocole_La_Heve_Lejard_10_03_2017.pdf) -
    AH 2500FT AMSL
    AL SFC
    DP 49:31:1N 0:0:3W
    DP 49:37:30N 0:8:18E
    DP 49:35:8N 0:12:47E
    DP 49:28:36N 0:4:24E
    DP 49:31:1N 0:0:3W

    # ----------------------------------
    #Extract of poaff geoJSON file
    # ----------------------------------
    {"type": "Feature",
    "properties": {"nameV": "RMZ LE HAVRE (FFVL-Prot)", "class": "RMZ", "type": "RMZ", "codeActivity": "FFVL-Prot", "lower": "SFC", "upper": "2500FT AMSL", "lowerM": 0, "upperM": 762, "desc": "LE HAVRE AFIS SKED", "activationDesc": "(Pascal Bazile: Voir protocole https://federation.ffvl.fr/sites/ffvl.fr/files/Protocole_La_Heve_Lejard_10_03_2017.pdf) - ", "GUId": "LFSRMZOH", "UId": "25090928", "id": "LFSRMZOH", "stroke": "#f07800", "stroke-width": 2, "stroke-opacity": 0.8, "fill": "#f07800", "fill-opacity": 0},
    "geometry": {"type": "Polygon", "coordinates": [[[-0.000833, 49.516944], [0.138333, 49.625], [0.213056, 49.585556], [0.073333, 49.476667], [-0.000833, 49.516944]]]}},

    # ----------------------------------
    # convert format with (lat, lon)
    # ----------------------------------
    coords = ((49.516944, -0.000833),(49.625, 0.138333),(49.585556, 0.213056),(49.476667, 0.073333),(49.516944, -0.000833))

    # ----------------------------------
    # Compare software
    # ----------------------------------
    generate with GPSdump - {gfmHdDkbTwdZnuFarMpgThhZuzFnnM
    genrate with localfct - {gfmHdDkbTwdZpuF_rMpgTfhZwzFnnM

    # ----------------------------------
    # Polygon format for Google Maps API
    # ----------------------------------
    // RMZ LE HAVRE (FFVL-Prot)
    var polygon = new google.maps.Polygon({
    map:map, path:google.maps.geometry.encoding.decodePath('{gfmHdDkbTwdZpuF_rMpgTfhZwzFnnM')
    //, strokeColor: "#FF0000", strokeOpacity: 0.5, strokeWeight: 1, fillColor: "#00FF00", fillOpacity: 0.10
    });
    //polygon.bounds  = new google.maps.LatLngBounds(new google.maps.LatLng(48.480556, 1.986667), new google.maps.LatLng(49.232778, 3.060833));
    polygon.altHigh = 2500;
    polygon.altLow  = 0;
    attachPolygonInfoBox(polygon, infoBox, 'RMZ LE HAVRE (FFVL-Prot)<br />Class RMZ<br />Upper:&nbsp; 2500 ft AMSL<br />Lower:&nbsp; SFC');
    polygon.GUId="LFSRMZOH";
    polygon.airspaceClass="RMZ";
    polygon.VName="RMZ LE HAVRE (FFVL-Prot)";
    polygons.push(polygon);

    """
