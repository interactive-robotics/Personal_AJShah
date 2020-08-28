/********** Randomness & other tools **********/
// Given an array of arrays, merges all sub-arrays into a single array
var mergeArray = function(arrOfarr) {
  return [].concat.apply([], arrOfarr);
}

// Given n, returns a random permutation of {1, ... , n}
// if r_flag == false, then it returns the identity permutation.
var RandPerm = function(n,r_flag) {
  var rp = function(n,i,A) {
    if (i == n-1) { return A; }
    else {
      var j = randomInteger(n-i) + i;
      var B = ((i==j) ? A :
               mergeArray([A.slice(0,i), [A[j]], A.slice(i+1,j), [A[i]], A.slice(j+1,n)]));
      return rp(n, i+1, B);
    }
  }
  return (r_flag ? rp(n,0,_.range(n)) : _.range(n));
}

// Given an array of formulas, returns the "and" of the formulas.
// Optimizes a little bit:
// -- If any formula is 'false', then result is 'false'.
// -- Removes all formulas that are 'true'.
var GlobalAnd = function(formulas) {
  if (any(function(x) { return x[0] == 'false'; }, formulas)) { return ['false']; }
  else {
    var forms = filter(function(x) { return (x[0] != 'true'); }, formulas);
    return ((forms.length==0) ? ['true'] :
            ((forms.length==1) ? forms[0] : mergeArray([['and'], forms])));
  }
}

// Given an array, returns a subset of it, by including each element w.p. 1/2.
var SubsetSampler = function(A) {
  var SS = function(i, B) {
    return ((i == A.length) ? B : SS(i+1, (flip(0.5) ? B : B.concat(A[i]))));
  }
  return SS(0,[]);
}


// Given n, divides the set {1, ... , n} into random subsets.
// Parameter p controls the preference among smaller vs larger subsets.
var DivideIntoSubsets = function(n, p) {
  var rp = RandPerm(n, true);
  var DIS = function(i, ans) {
    if (i==n) { return ans; }
    else { return flip(p) ? DIS(i+1, ans.concat([[rp[i]]])) :
    DIS(i+1, ans.slice(0,ans.length-1).concat([ans[ans.length-1].concat(rp[i])])); }
  }
  return DIS(1, [[rp[0]]]);
}

// Given nThreats and nWaypoints, generates set of Atoms present in LTL formulas.
var LTL_AtomsGen = function(nThreats, nWaypoints) {
  var Threats = mapN(function(i) {return 'T' + i; }, nThreats)
  var Waypoints = mapN(function(i) {return 'W' + i; }, nWaypoints)
  var Positionals = mapN(function(i) {return 'P' + i; }, nWaypoints)
  return mergeArray([Threats, Waypoints, Positionals]);
}

// Formula to encode that Waypoint B is visited strictly after Waypoint A.
// It is allowed to visit Waypoint B before Waypoint A, as long as Waypoint B is visited later as well.
var AbeforeB = function (A, B) {
  //var ifAthenFA = function(A) { return ['imp', ['P'+A], ['F', ['W'+A]]]; }
  //return ['R', ['not', ifAthenFA(A)], ifAthenFA(B)];
  return ['imp', ['P'+A] , ['U', ['not',['W'+B]], ['W'+A]]];
}

// Given an array S, apply the ordering constraints from left to right.
var OrderSubset = function(S) {
  var GetOrders = function(){
    var Orders = mapN(function(j) {
        return map(function(e){
          return [S[j],e];
        }, S.slice(j+1))
      }, S.length-1)
    var orders = reduce(function(x,acc){return acc.concat(x)},[],Orders)
    return orders
  }

  var GetFormulas = function(Orders){
    return map(function(x){AbeforeB(x[0],x[1]);}, Orders)
  }

  var orders = GetOrders(S)
  var formulas = GetFormulas(orders)

  var value = {
    orderings:orders,
    formulaList:formulas
  }

  return value
}


var DivideIntoTrees = function(n) {
  var rp = RandPerm(n, true);
  var InsertInForest = function(forest, e) {
    var Ps = map(function(t) { return t.size + 1; }, forest).concat(5);
    var Vs = _.range(forest.length+1);
    var i = categorical({ps: Ps, vs: Vs});
    if (i == forest.length) {
      return forest.concat({size: 1, val: e, children: []});
    } else {
      var newChild = {
        size: forest[i].size+1,
        val: forest[i].val,
        children: InsertInForest(forest[i].children, e)
      };
      return mergeArray([forest.slice(0,i), [newChild], forest.slice(i+1,forest.length)]);
    }
  }
  var DIT = function(i) {
    return ((i == 0) ? InsertInForest([], rp[0]) : InsertInForest(DIT(i-1), rp[i]));
  }
  return DIT(n-1);
}



var ForestToOrderings = function(forest) {

  /* Define the helper functions */
  var GetChildren = function(e){
    var children = map(function(child){return child.val}, e.children)
    return children
  }

  var GetDescendants = function(e){
    var temp = e.children
    if (temp.length == 0){
      return []
    } else{
      var children = GetChildren(e)
      var otherDescendants = map(GetDescendants, e.children);
      var descendants = mergeArray([children, mergeArray(otherDescendants)])
      return descendants
    }
  }

  var AllOrderings = function(e){
    var descendants = GetDescendants(e);
    var Orderings = map(function(descendant){return [e.val, descendant]}, descendants)
    return Orderings
  }

  var OrderTree = function(e){
    /* If the tree is empty return an empty set */
    if (e.children.length == 0){
      return []
    } else{
      var RootOrderings = AllOrderings(e);
      var OtherOrderings = map(AllOrderings,e.children)
      var TreeOrderings = mergeArray([RootOrderings, mergeArray(OtherOrderings)]);
      return TreeOrderings
    }
  }

  return mergeArray(map(OrderTree, forest))
}



/********** LTL Formula Checker **********/

// Given a "word", "formula" and "list of atoms", returns whether "word" satisfies "formula".
var SatChecker = function (word, formula, listofatoms) {
  var w = word.signal;
  var isAtom = function(s) { return listofatoms.includes(s); }
  var SC = dp.cache(function(f, t) {
    if (f.length == 0) { return true; }
    if (isAtom(f[0])) { return (w(f[0], t)); }
    if (f[0] == 'true') { return true; }
    if (f[0] == 'false') { return false; }
    if (f[0] == 'not') { return !(SC(f[1],t)); }
    if (f[0] == 'and') { return all(function(fi) { return SC(fi,t); }, f.slice(1,f.length)); }
    if (f[0] == 'or') { return any(function(fi) { return SC(fi,t); }, f.slice(1,f.length)); }
    if (f[0] == 'imp') { return (!SC(f[1],t) || SC(f[2],t)); }
    if (t == word.length - 1) {
      if (f[0] == 'X' || f[0] == 'G' || f[0] == 'F') { return SC(f[1],t); }
      if (f[0] == 'U') { return SC(f[2],t); }
      if (f[0] == 'wU') { return (SC(f[2],t) || SC(f[1],t)); }
      if (f[0] == 'R') { return SC(f[2],t); }
    } else {
      if (f[0] == 'X') { return (SC(f[1],t+1)); }
      if (f[0] == 'G') { return (SC(f[1],t) && SC(['G',f[1]],t+1)); }
      if (f[0] == 'F') { return (SC(f[1],t) || SC(['F',f[1]],t+1)); }
      if (f[0] == 'U') { return (SC(f[2],t) || (SC(f[1],t) && SC(['U',f[1],f[2]],t+1))); }
      if (f[0] == 'wU') { return (SC(f[2],t) || (SC(f[1],t) && SC(['wU',f[1],f[2]],t+1))); }
      if (f[0] == 'R') { return (SC(f[2],t) && (SC(f[1],t) || SC(['R',f[1],f[2]],t+1))); }
    }
    return true;
  });
  return SC(formula,0);
}

/********** Custom LTL Formula Generator **********/





// Samples a subset of threats, a subset of waypoints and a subset of ordering
var LTL_Sampler4 = function(nThreats, nWaypoints) {
  /* Generate the random choices */
  var subs = DivideIntoSubsets(nWaypoints, 0.7); //Subsets for orderings
  var Threats = SubsetSampler(_.range(nThreats)); //Threat choices
  var Waypoints = SubsetSampler(_.range(nWaypoints)) // Waypoint choices
  //console.log(subs);

  /*** Globally avoid threats ***/
  var ThreatAvoid = (Threats.length==0) ? [['true']] :
  map(function(i) {return ['G',['not', ['W' + i]]];} , Threats);

  /*** Eventually Waypoints ***/
  var FinallyWaypoints = (Waypoints.length==0) ? [['true']] :
  map(function(i) {return ['imp', ['P'+i] , ['F', ['W' + i]]];} , Waypoints)

  /*** Generate ordering ***/
  var Orders = map(OrderSubset, subs);
  var OrderWaypointsFormula = mergeArray(map(function(x) { return x.formulaList; }, Orders));
  var OrderWaypointsList = mergeArray(map(function(x) { return x.orderings; }, Orders));

  /*** Combine and return ***/
  return {
    nThreats: Threats.length,
    threats: Threats,
    nWaypoints: Waypoints.length,
    Waypoints: Waypoints,
    nOrderings: OrderWaypointsList.length,
    orderings: OrderWaypointsList,
    formula: GlobalAnd(mergeArray([ThreatAvoid, FinallyWaypoints, OrderWaypointsFormula]))
  };
}





/********** LTL Formula Inference **********/

// Given JSON object "data", converts it to a "word" as required by SatChecker.
var GenerateWord = function(data) {
  var Tht = data.hasOwnProperty('ThreatPredicates') ? data.ThreatPredicates : [];
  var WpP = data.WaypointPredicates;
  var Pos = data.hasOwnProperty('PositionPredicates') ? data.PositionPredicates : [];
  return {
    length: WpP[0].length,
    signal: function(sig, time) {
      var ctg = sig[0];
      var ind = Math.round(sig.slice(1,sig.length));
      if(ctg == 'T') { return Tht[ind][time]; }
      if(ctg == 'W') { return WpP[ind][time]; }
      if(ctg == 'P') { return !Pos[ind][time]; }
    }
  };
}

// Defines a complexity parameter for any formula with certain number of threats, waypoints and orderings.
var ComplexityFactorCustom = function(nT, nW, nO){
  var val = Math.log(2)*(nO+nT+nW);
  return val
}

var ComplexityFactorConstant = function(nT, nW, nO){
  var val = 0;
  return val
}

// makeModelQuery for a single JSON object "data".
var makeModelQuery = function(data) {
  var num_t = data.hasOwnProperty('ThreatPredicates') ? data.ThreatPredicates.length : 0;
  var num_w = data.WaypointPredicates.length;
  return function() {
    var word = GenerateWord(data);
    var Formula = LTL_Sampler2(num_t, num_w);
    var listofatoms = LTL_AtomsGen(num_t, num_w);
    var complexity = ComplexityMeasure(Formula.nThreats, Formula.nWaypoints, Formula.nOrderings);
    factor(SatChecker(word, Formula.formula, listofatoms) ? complexity : -4);
    return Formula.formula;
  }
}

// makeModelQuery for multiple files.
var makeModelQueryFull = function(FullData, sampler, ComplexityMeasure){
  //var num_t = FullData[0].Data.hasOwnProperty('ThreatPredicates') ? FullData[0].ThreatPredicates.length : 0;
  var num_t = FullData[0].Data.WaypointPredicates.length;
  var num_w = FullData[0].Data.WaypointPredicates.length;
  return function(){
    var Formula = sampler(num_t, num_w);
    var complexity = ComplexityMeasure(Formula.nThreats, Formula.nWaypoints, Formula.nOrderings);
    var listofatoms = LTL_AtomsGen(num_t, num_w);

    var SatCheckerTrajectory = function(data){
      var word = GenerateWord(data.Data);
      //factor(SatChecker(word, Formula.formula, listofatoms) ? complexity : -5);
      //var val = SatChecker(word, Formula.formula, listofatoms) ? complexity : -10

      var determineVal = function(word, Formula, listofatoms){
        if (data.Label == true){
          var val = SatChecker(word, Formula.formula, listofatoms)==data.Label ? complexity : -4*Math.log(2)*(num_t + num_w + 0.5*(num_w)*(num_w-1))
          return val
        } else{
            var val = SatChecker(word, Formula.formula, listofatoms)==data.Label ? 0 : -4*Math.log(2)*(num_t + num_w + 0.5*(num_w)*(num_w-1))
            return val
        }
      }
      var val = determineVal(word, Formula, listofatoms)
      //console.log(val)
      //console.log(SatChecker(word, Formula.formula, listofatoms))
      factor(val)
    }

    map(SatCheckerTrajectory, FullData)
    return Formula.formula;
  }
}


/********** Data Import **********/
//define full path to project folder
//var path = "/Users/pritishkamath/Documents/GitHub/9.660-Project/"

//single data file
//var data = json.read(path + "SimDomain/ThreatData/Predicates_1.json");

//Multiple trajectories Import

//var filenames = fs.filenames('Data/')
//console.log(filenames)
var GetData = function(dir, nTraj){
  var filenames = fs.filenames(dir)
  var n = (nTraj <= filenames.length) ? nTraj : filenames.length
  //console.log(filenames.slice(0,n))

  var GetFileData = function(filename){
    return json.read(dir + '/' + filename)
  }

  return map(GetFileData, filenames.slice(0,n))
}

/********** Testing Data IO **********/
//var Data = GetData('Data')
//console.log(Data)

/********* Inference Code *********/

var Complexity = ComplexityFactorCustom
var dataPath = argv.dataPath
var outPath = argv.outPath
var nBurn = argv.nBurn
var nSamples = argv.nSamples
var nTraj = argv.nTraj
//console.log(dataPath)
var DemoData = GetData(dataPath, nTraj)
//console.log(DemoData)

// DO Inference

//console.log('Number of demo examples: ')
//console.log(DemoData.length)
//console.log(nSamples)
var model = makeModelQueryFull(DemoData, LTL_Sampler4, Complexity)
var dist = Infer({method:'MCMC', samples:nSamples, burn:nBurn, verbose:true}, model)
var filename = outPath + '/batch_posterior.json'
json.write(filename, dist)



//
// var GetRunData = function(nTraj,Data){
//   var filenames = map(function(i){return 'Predicates_'+ i}, _.range(1,nTraj+1))
//   var path = 'SimDomain/' + Data + '/';
//
//   var GetData = function(path,filename){
//     var data = json.read(path + filename + '.json');
//     return data;
//   }
//
// var FullData = map(function(filename){return GetData(path,filename);},filenames)
// return FullData
// }




/********* Inference Code ********/


//run sims for Custom complexity
// var Complexity = ComplexityFactorCustom
// var ComplexityStr = 'Custom'
// var Data = argv.Data
// var nTraj = argv.nTraj
//
// var nBurn = argv.nBurn
// var nSamples = argv.nSamples


//Get Data
// var FullData = GetRunData(nTraj,Data)
//console.log(FullData)

//Do Inference




// console.log(nTraj)
// console.log(Data)
// console.log(Complexity)
// var model = makeModelQueryFull(FullData, LTL_Sampler5, Complexity)
// //var dist = Infer({method:'enumerate'}, model)
// var dist = Infer({method:'MCMC', samples:nSamples, burn:nBurn, verbose:true}, model)
// //var sampleFormula = sample(dist)
// var ComplexityStr = 'Custom'
// var filename = Data + '_OutputDist_Sampler5_'+ComplexityStr+'_'+nTraj+'.json'
// json.write(filename,dist)
