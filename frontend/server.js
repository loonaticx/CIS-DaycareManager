// load the things we need
var express = require('express');
var app = express();
const bodyParser = require('body-parser');

// required module to make calls to a REST API
const axios = require('axios');

app.use(bodyParser.urlencoded());

// set the view engine to ejs
app.set('view engine', 'ejs');

// use res.render to load up an ejs view file
// https://www.w3schools.com/bootstrap/tryit.asp?filename=trybs_ref_js_dropdown_multilevel_css&stacked=h


app.get('/', function (req, res) {
    res.render('pages/index', {});
});


app.get('/facilities', function (req, res) {
    axios.get(`http://127.0.0.1:5000/api/lookup/facilities`)
        .then((response) => {
            console.log(response)
            var facilities = response.data;
            // console.log(response);
            // use res.render to load up an ejs view file
            res.render('pages/facilities', {
                facilities: facilities,
            });
        })
        .catch((err) => {
            res.render('pages/error');
        });;
});

app.get('/facility', function (req, res) {
    axios.get(`http://127.0.0.1:5000/api/lookup/facilities`)
        .then((response) => {
            var facilities = response.data;
            var tagline = "Top 10 awesome moments of ALL time";
            // console.log(response);
            // use res.render to load up an ejs view file
            res.render('pages/facilities', {
                facilities: facilities,
                tagline: tagline
            });
        })
        .catch((err) => {
            res.render('pages/error');
        });;
});


/*
Classroom directory of a facility
*/
app.get('/facility/:facilityId', function (req, res) {
    var facilityId = req.params['facilityId'];
    axios.get(`http://127.0.0.1:5000/api/lookup/${facilityId}/`)
        .then((response) => {
            var data = response.data;
            var metadata = data.metadata;
            var content = data.content;
            // use res.render to load up an ejs view file
            res.render('pages/profile_facility', {
                classrooms: content,
                facilityId: metadata.facility_uuid, // UUID
                facilityName: metadata.facility_name,
                metadata: metadata,
                apiPath: `${facilityId}`
            });
        })
        .catch((err) => {
            res.render('pages/error');
        });
});
// https://expressjs.com/en/guide/routing.html
/*
Classroom Portal
List all teachers
*/
app.get('/facility/:facilityId/:classroomId', function (req, res) {
    var facilityId = req.params['facilityId'];
    var classroomId = req.params['classroomId'];
    console.log(classroomId);
    axios.get(`http://127.0.0.1:5000/api/lookup/${facilityId}/${classroomId}`)
        .then((response) => {
            var data = response.data;
            var metadata = data.metadata;
            var content = data.content;

            console.log(response);
            // use res.render to load up an ejs view file
            res.render('pages/profile_class', {
                classinfo: content,
                classroomId: content.uuid, // UUID
                classroomCapacity: content.capacity,
                classroomName: content.name,
                facilityId: metadata.facility_uuid, // UUID
                facilityName: metadata.facility_name,
                teachers: content["Teachers"],
                openSpots: metadata.unoccupied_slots,
                apiPath: `${facilityId}/${classroomId}`
            });
        })
        .catch((err) => {
            res.render('pages/error');
        });
});

/*
Teacher Profile
*/
app.get('/facility/:facilityId/:classroomId/:teacherId', function (req, res) {
    var facilityId = req.params['facilityId'];
    var classroomId = req.params['classroomId'];
    var teacherId = req.params['teacherId'];
    axios.get(`http://127.0.0.1:5000/api/lookup/${facilityId}/${classroomId}/${teacherId}`)
        .then((response) => {
            var data = response.data;
            var metadata = data.metadata;
            var content = data.content;

            console.log(data);

            // use res.render to load up an ejs view file
            res.render('pages/profile_teacher', {
                teacherinfo: content,
                teacherId: content.uuid, // UUID
                children: content["Children"],
                facilityId: metadata.facility_uuid, // UUID
                facilityName: metadata.facility_name,
                classroomName: metadata.classroom_name,
                classroomId: metadata.classroom_uuid,
                showCreateButton: false, // wil be used to determine if user can add/generate
                apiPath: `${facilityId}/${classroomId}/${teacherId}`

            });
        })
        .catch((err) => {
            res.render('pages/error');
        });
});

/*
Child Profile
*/

app.get('/facility/:facilityId/:classroomId/:teacherId/:childId', function (req, res) {
    var facilityId = req.params['facilityId'];
    var classroomId = req.params['classroomId'];
    var teacherId = req.params['teacherId'];
    var childId = req.params['childId'];
    axios.get(`http://127.0.0.1:5000/api/lookup/${facilityId}/${classroomId}/${teacherId}/${childId}`)
        .then((response) => {
            var data = response.data;
            var metadata = data.metadata;
            var content = data.content;

            console.log(data);

            // use res.render to load up an ejs view file
            res.render('pages/profile_child', {
                childinfo: content,
                childId: content.uuid, // UUID
                ids: `${facilityId}/${classroomId}/${teacherId}/${childId}`,
                apiPath: `${facilityId}/${classroomId}/${teacherId}/${childId}`
            });
        })
        .catch((err) => {
            res.render('pages/error');
        });
});




app.listen(8080);
console.log('8080 is the magic port');