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
        #return encoded_points_str #, encoded_levels_str
        return encoded_points_str.replace("\\", "\\"*2)

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
        return encoded_points_str.replace("\\", "\\"*2), encoded_levels_str

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

    #Bug - GUId="LFR164A2" ; pol.nameV="R 164 A2 Info(130.275)";
    coordsBug0 = [[6.605278, 48.613611], [6.61663, 48.614872], [6.628118, 48.615383], [6.63963, 48.615199], [6.651068, 48.614322], [6.662336, 48.612757], [6.673342, 48.61052], [6.683992, 48.607628], [6.694198, 48.604105], [6.703874, 48.599981], [6.71294, 48.59529], [6.72132, 48.590072], [6.728945, 48.584371], [6.735752, 48.578232], [6.741683, 48.571709], [6.746689, 48.564855], [6.75073, 48.557728], [6.753771, 48.550386], [6.755789, 48.542892], [6.756766, 48.535307], [6.756696, 48.527695], [6.755578, 48.520118], [6.753424, 48.512641], [6.75025, 48.505324], [6.746085, 48.498229], [6.740963, 48.491416], [6.734926, 48.484939], [6.728026, 48.478854], [6.72032, 48.47321], [6.711872, 48.468055], [6.702752, 48.46343], [6.693036, 48.459376], [6.682805, 48.455924], [6.672143, 48.453104], [6.66114, 48.450938], [6.649885, 48.449446], [6.638473, 48.448639], [6.626997, 48.448524], [6.615553, 48.449102], [6.604236, 48.450368], [6.593139, 48.452312], [6.582354, 48.454917], [6.57197, 48.458162], [6.562075, 48.462021], [6.552748, 48.46646], [6.544069, 48.471444], [6.53611, 48.47693], [6.528935, 48.482875], [6.522607, 48.489227], [6.517176, 48.495935], [6.512689, 48.502943], [6.509183, 48.510193], [6.506688, 48.517624], [6.505225, 48.525174], [6.504807, 48.532782], [6.505437, 48.540383], [6.507111, 48.547914], [6.509815, 48.555314], [6.517932, 48.552763], [6.52629, 48.550952], [6.530583, 48.550317], [6.539311, 48.549601], [6.548105, 48.549633], [6.556821, 48.550412], [6.565313, 48.551926], [6.569431, 48.552951], [6.573442, 48.554149], [6.577327, 48.555516], [6.581072, 48.557045], [6.58466, 48.558731], [6.588077, 48.560566], [6.591309, 48.562542], [6.594342, 48.564652], [6.597164, 48.566887], [6.599762, 48.569238], [6.602127, 48.571694], [6.604247, 48.574246], [6.606116, 48.576883], [6.607723, 48.579594], [6.609064, 48.582368], [6.610132, 48.585194], [6.610923, 48.588059], [6.611434, 48.590952], [6.611661, 48.59386], [6.611605, 48.596772], [6.611266, 48.599676], [6.610644, 48.602559], [6.609743, 48.60541], [6.608566, 48.608216], [6.607118, 48.610967], [6.605405, 48.61365], [6.605278, 48.613611]]
    bug0 = geoCod.encode(coordsBug0)
    print ("\nBug0:" + bug0)
    #>> Bug0:azugH}aig@{F_fAeBwfAd@_gAlDmfAxHmeA|LycAbQqaA~Tw~@vXo{@h\uw@r_@ks@rb@sn@je@qi@xg@ad@xi@g^pk@iXzl@_Rxm@qKln@cEpn@Ljn@~Etm@lLvl@xRjk@`Ypi@~^ng@vd@~d@bj@fb@bo@f_@xs@z[~w@jXv{@pT|~@rPraApLvcAhHjeA`DhfATvfAsBnfA{FveAeKjdAgOjbAiSz_AcWz|@wZhy@c^fu@ia@tp@cd@zk@uf@pf@}h@|`@yj@`[il@zTmm@rNen@bHqn@rAon@}Ban@oIgm@{O|Nwq@hJgs@~ByYlCqu@E}u@{Cou@mHat@mEwXmFaXqGgWqHmVqImUmJiTkKeSeL_R}LsPuMgOkNwM}NgLoOuJ}OaIiPkGuPuE{P}CcQeBeQm@eQJcQbA_QzB{PrDoPjFeP`HyOtIFX
    coordsBug1 = []
    for pt in coordsBug0:
        coordsBug1 += [[pt[1], pt[0]]]
    #print (coordsBug1)
    bug1, lev1 = geoCod.encode_pairs(coordsBug1)
    #print ("\nBug1:" + bug1)
    assert bug0 == bug1


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
