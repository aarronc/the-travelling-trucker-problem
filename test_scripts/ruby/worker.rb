require 'time'
require 'json'
require 'net/http'

def next_lexicographic_permutation(x)    return false if x.length<2 # Don't even bother if this is the case   
  i = x.length-2

  while i >= 0 do 
    if x[i] < x[i+1]
      break
    else 
      i -= 1
    end
    return false if i < 0 # This would mean that we are at final permutation.
  end

  j = x.length - 1

  while j > i do 
    break if x[j] > x[i]
    j -= 1
  end 

  swap(x, i, j)
  reverse(x, i+1)
  return x 
  end


  def swap(arr, x, y) # exchanges elements in the array in-place (destructively).  This changes the original array
    temp = arr[x] 
    arr[x] = arr[y]
    arr[y] = temp
  end


  def reverse(arr, i)
    if i>=arr.length-1 # either we are at the last element, or i is too high to exist in the array
      return
    end

    j = arr.length - 1
    
    while i < j do 
      swap(arr, i, j) # using our #swap helper method
      i+=1
      j-=1
    end
  end

def add_comma(number)
  number = number.to_s.chars.to_a.reverse.each_slice(3).map(&:join).join(",").reverse
  return number
end

def post(url, payload)
	uri = URI.parse(url)
	http = Net::HTTP.new(uri.host, uri.port)
	request = Net::HTTP::Post.new(uri.request_uri)
	request["Accept"] = "application/json"
	request.content_type = "application/json"
	request.body = payload
  puts "Sent result home..."
	return http.request(request)
end

VERSION = "S0.0.1"

uri = URI.parse("http://136.244.76.145:4567/work.json")
lookup = {0=>{"name"=>"van Maanen's Star", "x"=>-6.3125, "y"=>-11.6875, "z"=>-4.125}, 1=>{"name"=>"Wolf 124", "x"=>-7.25, "y"=>-27.1562, "z"=>-19.0938}, 2=>{"name"=>"Midgcut", "x"=>-14.625, "y"=>10.3438, "z"=>13.1562}, 3=>{"name"=>"PSPF-LF 2", "x"=>-4.40625, "y"=>-17.1562, "z"=>-15.3438}, 4=>{"name"=>"Wolf 629", "x"=>-4.0625, "y"=>7.6875, "z"=>20.0938}, 5=>{"name"=>"LHS 3531", "x"=>1.4375, "y"=>-11.1875, "z"=>16.7812}, 6=>{"name"=>"Stein 2051", "x"=>-9.46875, "y"=>2.4375, "z"=>-15.375}, 7=>{"name"=>"Wolf 25", "x"=>-11.0625, "y"=>-20.4688, "z"=>-7.125}, 8=>{"name"=>"Wolf 1481", "x"=>5.1875, "y"=>13.375, "z"=>13.5625}, 9=>{"name"=>"Wolf 562", "x"=>1.46875, "y"=>12.8438, "z"=>15.5625}, 10=>{"name"=>"LP 532-81", "x"=>-1.5625, "y"=>-27.375, "z"=>-32.3125}, 11=>{"name"=>"LP 525-39", "x"=>-19.7188, "y"=>-31.125, "z"=>-9.09375}, 12=>{"name"=>"LP 804-27", "x"=>3.3125, "y"=>17.8438, "z"=>43.2812}, 13=>{"name"=>"Ross 671", "x"=>-17.5312, "y"=>-13.8438, "z"=>0.625}, 14=>{"name"=>"LHS 340", "x"=>20.4688, "y"=>8.25, "z"=>12.5}, 15=>{"name"=>"Haghole", "x"=>-5.875, "y"=>0.90625, "z"=>23.8438}, 16=>{"name"=>"Trepin", "x"=>26.375, "y"=>10.5625, "z"=>9.78125}, 17=>{"name"=>"Kokary", "x"=>3.5, "y"=>-10.3125, "z"=>-11.4375}, 18=>{"name"=>"Akkadia", "x"=>-1.75, "y"=>-33.9062, "z"=>-32.9688}, 19=>{"name"=>"Hill Pa Hsi", "x"=>29.4688, "y"=>-1.6875, "z"=>25.375}, 20=>{"name"=>"Luyten 145-141", "x"=>13.4375, "y"=>-0.8125, "z"=>6.65625}, 21=>{"name"=>"WISE 0855-0714", "x"=>6.53125, "y"=>-2.15625, "z"=>2.03125}, 22=>{"name"=>"Alpha Centauri", "x"=>3.03125, "y"=>-0.09375, "z"=>3.15625}, 23=>{"name"=>"LHS 450", "x"=>-12.4062, "y"=>7.8125, "z"=>-1.875}, 24=>{"name"=>"LP 245-10", "x"=>-18.9688, "y"=>-13.875, "z"=>-24.2812}, 25=>{"name"=>"Epsilon Indi", "x"=>3.125, "y"=>-8.875, "z"=>7.125}, 26=>{"name"=>"Barnard's Star", "x"=>-3.03125, "y"=>1.375, "z"=>4.9375}, 27=>{"name"=>"Epsilon Eridani", "x"=>1.9375, "y"=>-7.75, "z"=>-6.84375}, 28=>{"name"=>"Narenses", "x"=>-1.15625, "y"=>-11.0312, "z"=>21.875}, 29=>{"name"=>"Wolf 359", "x"=>3.875, "y"=>6.46875, "z"=>-1.90625}, 30=>{"name"=>"LAWD 26", "x"=>20.9062, "y"=>-7.5, "z"=>3.75}, 31=>{"name"=>"Avik", "x"=>13.9688, "y"=>-4.59375, "z"=>-6.0}, 32=>{"name"=>"George Pantazis", "x"=>-12.0938, "y"=>-16.0, "z"=>-14.2188}}

b = {}
    0.upto(32) do |x|
      0.upto(32) do |y|
        if x == y 
          next
        else
          b["#{x}-#{y}"] = Math.sqrt(((lookup[x]['x'] - lookup[y]['x']) ** 2) + ((lookup[x]['y'] - lookup[y]['y']) ** 2) + ((lookup[x]['z'] - lookup[y]['z']) ** 2))
        end
      end
    end

while true do 
  http = Net::HTTP.new(uri.host, uri.port)
  response = http.request(Net::HTTP::Get.new(uri.request_uri))
  work = JSON.parse(response.body)
  
  identifier = work["identifier"]
  ip = work["perm"]
  
  lowest_total = 9999
  lowest_perm = []
  y = 0
  start = Time.now
  puts "Start @ #{start.utc.iso8601}"
  1.upto(10_000_000) do |x|
    y += 1
    if y < 1_000_000
    else
      puts "[#{Time.now.utc.iso8601}] Checkpoint #{add_comma(x)} / 10,000,000"
      y = 0
    end
    total = 0
    distance = b["#{ip[0]}-#{ip[1]}"] + b["#{ip[1]}-#{ip[2]}"] + b["#{ip[2]}-#{ip[3]}"] + b["#{ip[3]}-#{ip[4]}"] + b["#{ip[4]}-#{ip[5]}"] +
           b["#{ip[5]}-#{ip[6]}"] + b["#{ip[6]}-#{ip[7]}"] + b["#{ip[7]}-#{ip[8]}"] + b["#{ip[8]}-#{ip[9]}"] + b["#{ip[9]}-#{ip[10]}"] +
           b["#{ip[10]}-#{ip[11]}"] + b["#{ip[11]}-#{ip[12]}"] + b["#{ip[12]}-#{ip[13]}"] + b["#{ip[13]}-#{ip[14]}"] + b["#{ip[14]}-#{ip[15]}"] +
           b["#{ip[15]}-#{ip[16]}"] + b["#{ip[16]}-#{ip[17]}"] + b["#{ip[17]}-#{ip[18]}"] + b["#{ip[18]}-#{ip[19]}"] + b["#{ip[19]}-#{ip[20]}"] +
           b["#{ip[20]}-#{ip[21]}"] + b["#{ip[21]}-#{ip[22]}"] + b["#{ip[22]}-#{ip[23]}"] + b["#{ip[23]}-#{ip[24]}"] + b["#{ip[24]}-#{ip[25]}"] +
           b["#{ip[25]}-#{ip[26]}"] + b["#{ip[26]}-#{ip[27]}"] + b["#{ip[27]}-#{ip[28]}"] + b["#{ip[28]}-#{ip[29]}"] + b["#{ip[29]}-#{ip[30]}"] +
           b["#{ip[30]}-#{ip[31]}"] + b["#{ip[31]}-#{ip[32]}"]
      total = total + distance
    if total < lowest_total
      lowest_total = total
      lowest_perm = ip
      # puts "new lowest found on perm #{add_comma(x)} -> #{lowest_total.round(2)} -> #{ip.to_s.gsub!(" ","")}"
    end
    # sleep(60)
    # Perm should be interated at the end of the calculation
    ip = next_lexicographic_permutation(ip)
  end
  finish = Time.now
  puts "Finished @ #{finish.utc.iso8601}"
  puts "Lowest found this time -> #{lowest_total}"
  puts "permutation -> #{lowest_perm}"
  diff = finish - start
  puts "Time taken #{diff.round(3)} seconds"
  final = {}
  final['distance'] = lowest_total
  final['identifier'] = identifier
  final['perm'] = lowest_perm
  final['duration'] = diff
  final['finished_at'] = "#{Time.now.utc.iso8601}"
  final['version'] = VERSION
  sleep(0.1)
  post("http://136.244.76.145:4567/result", final.to_json)
end
