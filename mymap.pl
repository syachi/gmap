#!/usr/bin/env perl

use Mojolicious::Lite;

get '/' => sub {
  my $self = shift;
  $self->render('index');
};

get '/api/v1/addresses' => sub {
  my $self = shift;
  my $data = [
    {address => '北海道札幌市白石区菊水元町7条1丁目10−21'},
    {address => '北海道札幌市北区北18条西5丁目2−1'},
    {address => '北海道札幌市西区発寒3条6−1−3'},
    {address => '北海道札幌市北区北37条西4丁目2−6'},
    {address => '北海道札幌市北区北25条西5丁目2−8'},
    {address => '北海道札幌市北区北22条西5丁目2−32'},
    {address => '北海道札幌市手稲区西宮の沢5条1丁目14−10'},
  ];
  $self->render(json => $data);
};

app->start;

__DATA__

@@ index.html.ep
<!doctype html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>Show google map sample</title>
  <meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
  <script type="text/javascript" src="http://maps.google.com/maps/api/js?sensor=false"></script>
  <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
  <script type="text/javascript">
    $(function () {
      var mapcenter = new google.maps.LatLng(43.0631485, 141.3540735),
        geocoder = new google.maps.Geocoder(),
        myOptions = {
          zoom: 12,
          center: mapcenter,
          mapTypeId: google.maps.MapTypeId.ROADMAP
        },
        addresses = [],
        map = new google.maps.Map($("#map").get(0), myOptions);
      $.ajax({
        type: 'GET',
        url: 'api/v1/addresses',
        dataType: 'json',
        success: function(rows) {
          $.each(rows, function(i, row) {
            geocoder.geocode({"address": row.address, "region": "jp"}, function (results, status) {
              if (status !== google.maps.GeocoderStatus.OK) return;
              var marker = new google.maps.Marker({
                map: map,
                position: results[0].geometry.location
              });
            });
          });
        }
      });
    });
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
