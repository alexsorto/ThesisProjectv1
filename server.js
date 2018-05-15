var express = require('express');
var app = express();
var fs = require("fs");
var bodyParser = require('body-parser');


app.use(bodyParser.json()); 

app.use(bodyParser.urlencoded({ extended: true })); 

//Generates a transaction record
//

function generateTrx (companyId,type,clientuid,consoleId,amount,success) {
  fs.readFile( __dirname + "/" + "transactions.json", 'utf8', function (err, data) {

  var transactions = JSON.parse(data);

  var newTrx = {
    "companyid": companyId,
    "type": type,
    "client":clientuid,
    "consoleid":consoleId,
    "amount": amount,
    "datetime": Date.now,
    "success":success
  };

  transactions.push(newTrx);

  fs.writeFile('transactions.json', JSON.stringify(transactions), 'utf8', function(err){
    if(err) throw err;
  });

  });
}

//Get all users
app.get('/listUsers', function (req, res) {
   fs.readFile( __dirname + "/" + "users.json", 'utf8', function (err, data) {
       console.log( data );
       res.setHeader('Content-Type', 'application/json');

       res.end( data );
   });
})

//Get user by ID
app.get('/:id', function (req, res) {

  fs.readFile( __dirname + "/" + "users.json", 'utf8', function (err, data) {
     var users = JSON.parse( data );
     var user = users["user" + req.params.id] 
     console.log( user );
     res.setHeader('Content-Type', 'application/json');

     res.end( JSON.stringify(user));
  });
})


//Add credit to users account
app.post('/addCredit', function (req, res) {

  fs.readFile( __dirname + "/" + "users.json", 'utf8', function (err, data) {

     var users = JSON.parse(data);


     console.log(users);
     console.log(users["users"])
     var requestedUid = req.body["uid"];
     var amountChange = req.body["amount"];
     var companyId = req.body["companyid"];
     var consoleId = req.body["consoleid"];
     var selectedUser;

     for(var i = 0; i < users.length; i++) {

        var currentUser = (users[i]);
        
        // console.log(currentUser);
        // console.log(currentUser["credit"]);
        // console.log("Current user uid: " + currentUser["uid"]);
        // console.log("Requested UID: " + requestedUid);

        if(JSON.stringify(currentUser["uid"]) === JSON.stringify(requestedUid)) {
          console.log("Matchig user");
          var currentUserCredit = currentUser["credit"];
          currentUser["credit"] = currentUserCredit + amountChange;
          currentUser["success"] = 1;

          console.log("Account funded succesfully");

          
          selectedUser = currentUser;

          generateTrx(companyId,2,currentUser["uid"],consoleId,amountChange,1);


        }
     }

     fs.writeFile('users.json', JSON.stringify(users), 'utf8', function(err){
      if(err) throw err;
    })

     var user = "";
     res.setHeader('Content-Type', 'application/json');
     res.end( JSON.stringify(selectedUser));

  });
})


//Take credit off users account
app.post('/takeCredit', function (req, res) {
  // First read existing users.
  fs.readFile( __dirname + "/" + "users.json", 'utf8', function (err, data) {

     var users = JSON.parse(data);
    //  console.log(users);
    //  console.log(users["users"])
     var requestedUid = req.body["uid"];
     var amountChange = req.body["amount"];
     var companyId = req.body["companyid"];
     var consoleId = req.body["consoleid"];
     
     var selectedUser;

     for(var i = 0; i < users.length; i++) {

        var currentUser = (users[i]);

        if(JSON.stringify(currentUser["uid"]) === JSON.stringify(requestedUid)) {
          console.log("Matchig user");
          var currentUserCredit = currentUser["credit"];
          if(currentUserCredit >= amountChange) {
          currentUser["credit"] = currentUser["credit"] - amountChange;
          currentUser["success"] = 1;
          generateTrx(companyId,1,currentUser["uid"],consoleId,amountChange,1);

          console.log("Payment succesful");

          }
          if(currentUserCredit < amountChange) {
            currentUser["success"] = 0;
            generateTrx(companyId,1,currentUser["uid"],consoleId,amountChange,0);
            console.log("Payment declined");
          }

          selectedUser = currentUser;

        }
     }

     fs.writeFile('users.json', JSON.stringify(users), 'utf8', function(err){
      if(err) throw err;
    })

     var user = "";
     res.setHeader('Content-Type', 'application/json');
     res.end( JSON.stringify(selectedUser));

  });
})


var server = app.listen(8081, function () {

  var host = server.address().address
  var port = server.address().port

  console.log("Thesis server listening at: ", host, port)

})