const axios = require('axios');

const fetchImages = (count = 10) => {

    let type_input = document.getElementById('types_input').value;
    let type_select = document.getElementById('types_select').value;
  
    // URL: 'https://example.com/getimages.php?cat=' + type_input;
    let exampleURL = 'https://api.myjson.com/bins/7yftn?cat=' + type_input;
    alert("Stupid");
  
    axios.
    get(exampleURL).
    then(res => {
      console.log(res);
      // setImages([...images, ...res.data]);
      // setIsLoaded(true);
      // console.log(images);
    });
  };