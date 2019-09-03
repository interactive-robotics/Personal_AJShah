var GetData = function(dir, nTraj){
  var filenames = fs.filenames(dir)
  var n = (nTraj <= filenames.length) ? nTraj : filenames.length
  console.log(n)
  console.log(filenames.slice(0,n))


  var GetFileData = function(filename){
    return json.read(dir + '/' + filename)
  }

  return map(GetFileData, filenames.slice(0,n))
}

var n = argv.nTraj
var Data = GetData('Data/CompressedData', n)
console.log(Data)
