#!/usr/bin/env perl

use strict;
use warnings;
use utf8;
use Data::Section::Simple qw(get_data_section);
use JSON;
use LWP::UserAgent;
use Config::Any;
use Template;
use URI::Escape;

my $cfg = Config::Any->load_stems({stems => ["config"], use_ext => 1, flatten_to_hash => 1});
my ($map, $init) = ($cfg->{"config.json"}{"map"}, $cfg->{"config.json"}{"initial"});
my $ua = LWP::UserAgent->new();

## 処理部分 ##
# 住所データ取得
my @locdata = split(/\x0D\x0A|\x0D|\x0A/, get_data_section('shop.dat'));
# 住所から緯度経度を取得する
my @coords = getLocations(@locdata);

# HTMLの生成
my $html = get_data_section('index.html');
my $tt = Template->new();
print "Content-type: text/html".$/.$/;
print $tt->process(\$html, {
    initiallat => $init->{"lat"},
    initiallng => $init->{"lng"},
    COORD_ARRAY => JSON::encode_json(\@coords)
});

exit;



## @method getLocations
# 住所文字列リストからLat/Lngを取得し、リストを返却
# @param addresses [@] 住所文字列リスト
# @return [@] Location配列 hashref
sub getLocations {
    my @result;
    foreach (@_) {
        my $coords = getCoordinates($_);
        next if (not $coords);
        $coords->{"title"} =~ s/日本,\s+//msx;
        push(@result, $coords);
    }
    return @result;
}

sub getCoordinates {
    my $adrs = shift;
    $adrs =~ s/[\－─ー－−]/\-/msxgo;  # ハイフンを統一
    my $res = $ua->get(createUrl($map->{"apiurl"}, $map->{"apiopt"}, $adrs));
    # エラー処理
    return undef if (not $res->is_success);
    $res = decode_json($res->content);
    return undef if ($res->{status} ne 'OK');
    my $results = $res->{results};
    return undef if (ref($results) ne 'ARRAY' or @$results != 1);
    return {
        title => $results->[0]->{formatted_address}, # 整形後の住所文字列
        lat => $results->[0]->{geometry}->{location}->{lat}, #緯度
        lng => $results->[0]->{geometry}->{location}->{lng}  #軽度
    };
}

sub createUrl {
    return $_[0]."?".$_[1]."&address=".uri_escape_utf8($_[2]);
}

## データ部分 ##
__DATA__
@@ index.html
<!doctype html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>Show google map sample</title>
    <meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
    <script type="text/javascript" src="http://maps.google.com/maps/api/js?sensor=true"></script>
    <script type="text/javascript">
        window.onload = function () { initialize(); };
        function initialize() {
            var mapcenter = new google.maps.LatLng([% initiallat %], [% initiallng %]);
            var myOptions = {
                zoom: 12,
                center: mapcenter,
                mapTypeId: google.maps.MapTypeId.ROADMAP
            };
            var map = new google.maps.Map(document.getElementById("map"), myOptions);
            var markerData = [% COORD_ARRAY %]
            for (i = 0; i < markerData.length; i++){
                var marker = new google.maps.Marker({
                    position: new google.maps.LatLng(markerData[i].lat, markerData[i].lng),
                    title: markerData[i].title
                });
                marker.setMap(map);
            }
        }
    </script>
    <style type="text/css">
        html, body {margin: 0; padding: 0; height: 100%;}
        #map {width: 100%; height: 100%;}
    </style>
</head>
<body>
    <div id="map"></div>
</body>
</html>

@@ shop.dat
北海道札幌市白石区菊水元町7条1丁目10−21
北海道札幌市北区北18条西5丁目2−1
北海道札幌市西区発寒3条6−1−3
北海道札幌市北区北37条西4丁目2−6
北海道札幌市北区北25条西5丁目2−8
北海道札幌市北区北22条西5丁目2−32
北海道札幌市手稲区西宮の沢5条1丁目14−10
