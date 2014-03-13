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
# 住所から緯度経度を取得する
my @locdata = split(/\x0D\x0A|\x0D|\x0A/, get_data_section('shop.dat'));
my @coord;
foreach my $addr (@locdata){
    my $h = getCoordinates($addr);
    die("error") if (not $h);
    $h->{"title"} =~ s/日本,\s+//msx;
    push(@coord, $h);
}

# HTMLの生成
my $values = {
    initiallat => $init->{"lat"},
    initiallng => $init->{"lng"},
    COORD_ARRAY => JSON::encode_json(\@coord)
};
my $html = get_data_section('index.html');

my $tt = Template->new();
print "Content-type: text/html".$/.$/;
print $tt->process(\$html, $values);
exit;

## 関数 ##
sub getCoordinates {
    my $adrs = $_[0];
    $adrs =~ s/[\－─ー－−]/\-/msxgo;  # ハイフンを統一
    $adrs = uri_escape_utf8($adrs);
    my $res = $ua->get($map->{"apiurl"}."?".$map->{"apiopt"}."&address=".$adrs);    # Google mapsにアクセス
    # エラー処理
    return undef unless ($res->is_success);
    $res = decode_json($res->content);
    return undef unless ($res->{status} eq 'OK');
    my $results = $res->{results};
    return undef if(ref($results) ne 'ARRAY' or @$results != 1);
    # 値を返す
    return {
        title => $results->[0]->{formatted_address}, # 整形後の住所文字列
        lat => $results->[0]->{geometry}->{location}->{lat}, #緯度
        lng => $results->[0]->{geometry}->{location}->{lng}  #軽度
    };
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
