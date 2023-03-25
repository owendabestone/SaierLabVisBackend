from flask import Flask, request, render_template,make_response
from flask_restful import Resource, Api, reqparse
import assessionData
import pickle
import matplotlib.colors as mcolors
import random
import plotly.figure_factory as ff
from bs4 import BeautifulSoup
import urllib.request as urllib2
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
api = Api(app)
colors_bank= ['#F0F8FF', '#FAEBD7', '#00FFFF', '#7FFFD4', '#F0FFFF',
          '#F5F5DC', '#FFE4C4', '#000000', '#FFEBCD', '#0000FF',
          '#8A2BE2', '#A52A2A', '#DEB887', '#5F9EA0', '#7FFF00',
          '#D2691E', '#6495ED', '#FFF8DC', '#DC143C', '#00FFFF',
          '#00008B', '#008B8B', '#B8860B', '#A9A9A9', '#006400',
          '#A9A9A9', '#BDB76B', '#8B008B', '#556B2F', '#FF8C00',
          '#9932CC', '#8B0000', '#E9967A', '#8FBC8F', '#483D8B',
          '#2F4F4F', '#2F4F4F', '#00CED1', '#9400D3', '#FF1493',
          '#00BFFF', '#696969', '#696969', '#1E90FF', '#B22222',
          '#FFFAF0', '#228B22', '#FF00FF', '#DCDCDC', '#F8F8FF',
          '#FFD700', '#DAA520', '#808080', '#008000', '#ADFF2F',
          '#808080', '#F0FFF0', '#FF69B4', '#CD5C5C', '#4B0082',
          '#F0E68C', '#E6E6FA', '#FFF0F5', '#7CFC00', '#FFFACD',
          '#ADD8E6', '#F08080', '#E0FFFF', '#FAFAD2', '#D3D3D3',
          '#90EE90', '#D3D3D3', '#FFB6C1', '#FFA07A', '#20B2AA',
          '#87CEFA', '#778899', '#B0C4DE', '#FFFFE0', '#00FF00',
          '#32CD32', '#FAF0E6', '#FF00FF', '#800000', '#66CDAA',
          '#0000CD', '#BA55D3', '#9370DB', '#3CB371', '#7B68EE',
          '#00FA9A', '#48D1CC', '#C71585', '#191970', '#F5FFFA',
          '#FFE4E1', '#FFE4B5', '#FFDEAD', '#000080', '#FDF5E6',
          '#808000', '#6B8E23', '#FFA500', '#FF4500', '#DA70D6',
          '#EEE8AA', '#98FB98', '#AFEEEE', '#DB7093', '#FFEFD5',
          '#FFDAB9', '#CD853F', '#FFC0CB', '#DDA0DD', '#B0E0E6',
          '#800080', '#663399', '#FF0000', '#BC8F8F', '#4169E1',
          '#8B4513', '#FA8072', '#F4A460', '#2E8B57', '#FFF5EE',
          '#A0522D', '#C0C0C0', '#87CEEB', '#6A5ACD', '#708090', 
          '#00FF7F', '#4682B4', '#D2B48C', '#008080', '#D8BFD8',
          '#FF6347', '#40E0D0', '#EE82EE', '#F5DEB3', '#F5F5F5',
          '#FFFF00', '#9ACD32', '#0ead83', '#046582', '#045682',
          '#023c7a', '#02287a', '#7a026a', '#5a027a', '#856275',
          '#856275', '#628579', '#628567', '#38d64f', '#007812', 
          '#5d7355', '#d1d12a', '#b8716a', '#d6ab54', '#ba9750',
          '#5bba50', '#5adb98', '#1f7d4d', '#d6e349', '#d6e349',
          '#833991', '#5b3b61', '#10e682', '#1042e6', '#b7e610']

with open('query_length.pkl', 'rb') as file:
    query_length= pickle.load(file)
with open('db.pkl', 'rb') as file:
    db = pickle.load(file)
    
# class View(Resource):
#     def get(self):
#         class_ = int(request.args.get('class'))
#         family = int(request.args.get('family'))
            
#         output = db[class_][request.args.get('subclass')][family]
#         payload = {}
#         for subfamily in output:
#             payload[subfamily] = {}
#             for substrate in output[subfamily]:
#                 payload[subfamily][substrate]= {}
#                 id_ = 0 
#                 for dom in output[subfamily][substrate]:
#                     payload[subfamily][substrate][id_] = {
#                         'accession':dom.accession,
#                         'env_from':dom.env_from,
#                         'env_to':dom.env_to
#                     }
#                     id_+=1
#         return payload, 200  # return data and 200 OK code
    
    

class Plot(Resource):
    def get(self):
        class_ = int(request.args.get('class'))
        family = int(request.args.get('family'))
        try:
            database_subset = db[class_][request.args.get('subclass')][family]
        except:
            return make_response(render_template('404.html'), 200)
        
        df = {}
        pref =  str(class_) + '.' + request.args.get('subclass') + '.'  + str(family) + '.'
        for subfamily in database_subset:
            for substrate in database_subset[subfamily]:
                query = pref + str(subfamily) + '.' + str(substrate)
            
                df[query]= database_subset[subfamily][substrate]
        
        
        dataframe = []
        domains  = set()
        for protein in df:
            for dom in df[protein]:
                domains.add(dom.accession)
        for protein in df:
            dataframe.extend([dict(Task = protein,
                                Start = acc.env_from,
                                Finish = acc.env_to,
                                Resource = acc.accession) for acc in df[protein]] +
                             [dict(Task = protein,
                                Start = query_length[protein]-8,
                                Finish = query_length[protein],
                                Resource = "END")])

        colors = random.sample(colors_bank, len(domains))
        colors_map = {dom:color for dom ,color in zip(domains,colors) }
        colors_map['END']="#f02222"

        fig = ff.create_gantt(dataframe, show_colorbar = True, colors = colors_map,index_col='Resource',group_tasks=True)
        fig.update_layout(xaxis_type='linear', autosize=False, width=800, height=1000)
        fig.write_html("templates/plot.html", full_html = True) 
        return make_response(render_template('plot.html'), 200)  # return data and 200 OK code

# api.add_resource(View, '/view')
api.add_resource(Plot, '/plot')

if __name__ == '__main__':
    app.run(debug=False)  # run our Flask app