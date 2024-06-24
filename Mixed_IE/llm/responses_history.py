# Response from llama3-70b 1

responses = {
    "e2e":{
        "Role_Attr":{
            "llama3-70b":[
                '''
                Based on the high-frequency words provided, I infer the properties of the Restaurant role type as follows:

                Response: Name, Cuisine Type, Rating, Location, Price Range, Menu Offerings, Ambience, Family Friendliness, Average Price, Centre Location, Riverside View, Nearby Landmarks, Coffee Options, Indian/Italian Options, Pub Features.

                Please let me know if this meets your expectations!
                '''
                ,
                '''
                Based on the high-frequency words provided, I infer the properties of the Restaurant role type as follows:

                Response: Name, Cuisine Type, Rating, Location, Price Range, Customer Reviews, Family Friendliness, Menu Offerings, Average Price, Restaurant Type (e.g. Café, Pub), City Centre Location, Riverside Location, Indian/Italian/Other Specialty.
                '''
                ,
            ]
        },
        "KGs":{
            "llama3-70b":[
                '''
                Here is the Python class definition for the Restaurant Knowledge Graph:

                ```
                class Restaurant:
                    def __init__(self):
                        self.Name = None
                        self.Cuisine_Type = None
                        self.Rating = None
                        self.Location = None
                        self.Price_Range = None
                        self.Menu_Offerings = None
                        self.Ambience = None
                        self.Family_Friendliness = None
                        self.Average_Price = None
                        self.Centre_Location = None
                        self.Riverside_View = None
                        self.Nearby_Landmarks = None
                        self.Coffee_Options = None
                        self.Indian_Options = None
                        self.Italian_Options = None
                        self.Pub_Features = None
                ```

                Let me know if this meets your requirements!
                '''
                ,
            ]
        }
    },

    "rotowire":{
        "Role_Complete": {
            "llama3-70b" :[
                '''
                Based on the high-frequency words provided, I infer the following roles highly related to the Basketball Game event and the already known role "Team":

                1. Player
                2. Coach
                3. Referee
                4. Fan
                5. Scorekeeper
                6. Commentator
                7. Trainer

                These roles are closely related to the event and are likely to be involved in a basketball game. The high-frequency words suggest a focus on the game's statistics, team performance, and players' actions, which supports the inference of these roles.
                '''
                ,
                ]
            },
        "Role_Attr":{
            "llama3-70b":[
                '''
                Based on the high-frequency words provided, I infer that the properties of a Team of Basketball Game are:

                Name, Points Scored, Rebounds, Assists, Games Played, Minutes Played, Shooting Percentage, Field Goal Percentage, Three-Point Percentage, Free Throw Percentage, Steals, Blocks, Turnovers, Wins, Losses, Home Record, Away Record, Conference Record, Starting Lineup, Bench Strength, Scoring Average, Rebounding Average, Assist Average, Leading Scorers, Leading Rebounders, Leading Assist Providers.

                Let me know if this is accurate!
                '''
                ,
                '''
                Based on the high-frequency words provided, I infer the properties of a Player of Basketball Game to be:

                1. Name
                2. Points Per Game (PPG)
                3. Rebounds Per Game (RPG)
                4. Assists Per Game (APG)
                5. Minutes Played Per Game (MPPG)
                6. Field Goal Percentage (FG%)
                7. Free Throw Percentage (FT%)
                8. Three-Point Shooting Percentage
                9. Steals Per Game (SPG)
                10. Blocks Per Game (BPG)
                11. Turnovers Per Game (TPG)
                12. Games Played
                13. Wins-Losses Record
                14. Team(s) Played For
                15. Position (e.g., Point Guard, Center, etc.)
                16. Scoring Average
                17. Rebounding Average
                18. Assist Average
                19. Shooting Performance (e.g., high-scoring games, etc.)
                20. Career Highlights (e.g., awards, accolades, etc.)

                Please let me know if this is accurate or if you need further refinement!
                '''
            ]
        },
        "KGs":{
            "llama3-70b":[
                '''
                Based on the provided information, I will construct a Knowledge Graph for the Basketball Game event. Here is the response:

                    ```
                    class BasketballGame:
                        self.Name = None
                        self.Date = None
                        self.Location = None
                        self.Attendance = None
                        self.Score = None
                        self.Winning_Team = None
                        self.Losing_Team = None

                    class Team:
                        self.Name = None
                        self.Points_Scored = None
                        self.Rebounds = None
                        self.Assists = None
                        self.Games_Played = None
                        self.Minutes_Played = None
                        self.Shooting_Percentage = None
                        self.Field_Goal_Percentage = None
                        self.Three_Point_Percentage = None
                        self.Free_Throw_Percentage = None
                        self.Steals = None
                        self.Blocks = None
                        self.Turnovers = None
                        self.Wins = None
                        self.Losses = None
                        self.Home_Record = None
                        self.Away_Record = None
                        self.Conference_Record = None
                        self.Starting_Lineup = None
                        self.Bench_Strength = None
                        self.Scoring_Average = None
                        self.Rebounding_Average = None
                        self.Assist_Average = None
                        self.Leading_Scorers = None
                        self.Leading_Rebounders = None
                        self.Leading_Assist_Providers = None

                    class Player:
                        self.Name = None
                        self.Points_Per_Game = None
                        self.Rebounds_Per_Game = None
                        self.Assists_Per_Game = None
                        self.Minutes_Played_Per_Game = None
                        self.Field_Goal_Percentage = None
                        self.Free_Throw_Percentage = None
                        self.Three_Point_Shooting_Percentage = None
                        self.Steals_Per_Game = None
                        self.Blocks_Per_Game = None
                        self.Turnovers_Per_Game = None
                        self.Games_Played = None
                        self.Wins_Losses_Record = None
                        self.Teams_Played_For = None
                        self.Position = None
                        self.Scoring_Average = None
                        self.Rebounding_Average = None
                        self.Assist_Average = None
                        self.Shooting_Performance = None
                        self.Career_Highlights = None

                    class Play_Relationship:
                        self.Player = None
                        self.Team = None
                        self.Game = None
                        self.Minutes_Played = None
                        self.Points_Scored = None
                        self.Rebounds = None
                        self.Assists = None

                    class Team_Member_Relationship:
                        self.Team = None
                        self.Player = None
                        self.Position = None
                        self.Starting_Lineup = None

                    class Game_Participation_Relationship:
                        self.Game = None
                        self.Team = None
                        self.Score = None
                        self.Winning_Team = None
                        self.Losing_Team = None
                    ```

                    Note that I've identified the following roles and relations:

                    * Roles: BasketballGame, Team, Player
                    * Relations: Play_Relationship (between a player and a team in a game), Team_Member_Relationship (between a team and a player), Game_Participation_Relationship (between a team and a game)

                    Let me know if this meets your requirements or if you need further modifications!
                '''
            ]
        }
    },
    "CPL":{

        "Role_Complete":{
            "llama3-70b":[
                '''
                Based on the high-frequency words provided, I infer that the event "民间借贷案件" (Civil Loan Dispute) involves a legal dispute between individuals or organizations related to a loan agreement. 

                Given the already known roles ['原告' (Plaintiff), '被告' (Defendant)], I suggest the following highly related roles:

                1. 律师 (Lawyer) - represents the plaintiff or defendant in the legal dispute.
                2. 法院 (Court) - the institution responsible for hearing and judging the case.
                3. 裁判员 (Judge) - the official who presides over the court and makes judgments.
                4. 证人 (Witness) - individuals who provide testimony to support or refute claims in the case.
                5. 代理人 (Agent) - a person authorized to act on behalf of the plaintiff or defendant.
                6. 借款人 (Borrower) - the individual or organization that received the loan.
                7. 贷款人 (Lender) - the individual or organization that provided the loan.

                These roles are closely related to the event and the already known roles, and are likely to be involved in the legal dispute surrounding the civil loan.
                '''
                ,
            ]
        },
        "KGs":{
            "llama3-70b":[
                '''
                Based on the provided information, I will construct a Knowledge Graph for the event "民间借贷案件" (Civil Loan Dispute Case).

                Here is the Python class definition for the event:
                ```
                class CivilLoanDisputeCase:
                    self.Case_ID = None
                    self.Case_Name = None
                    self.Case_Description = None
                    self.Case_Status = None
                    self.Court = None
                    self.Judge = None
                    self.Trail_Date = None
                    self.Verdict = None

                class Plaintiff:
                    self.Name = None
                    self.Represented_By = None
                    self.Claims = None
                    self.Evidence = None

                class Defendant:
                    self.Name = None
                    self.Represented_By = None
                    self.Defense = None
                    self.Evidence = None

                class Lawyer:
                    self.Name = None
                    self.Representing = None
                    self.Legal_Arguments = None

                class Court:
                    self.Name = None
                    self.Jurisdiction = None
                    self.Location = None

                class Judge:
                    self.Name = None
                    self.Presiding_Over = None
                    self.Judgment = None

                class Witness:
                    self.Name = None
                    self.Testimony = None
                    self.Relation_To_Case = None

                class Agent:
                    self.Name = None
                    self.Authorized_By = None
                    self.Actions_Taken = None

                class Borrower:
                    self.Name = None
                    self.Loan_Amount = None
                    self.Loan_Purpose = None
                    self.Payment_History = None

                class Lender:
                    self.Name = None
                    self.Loan_Amount = None
                    self.Loan_Terms = None
                    self.Payment_History = None

                class Representation_Relationship:
                    self.Lawyer = None
                    self.Client = None
                    self.Start_Date = None
                    self.End_Date = None

                class Testimony_Relationship:
                    self.Witness = None
                    self.Case = None
                    self.Testimony_Date = None

                class Authorization_Relationship:
                    self.Agent = None
                    self.Principal = None
                    self.Authorization_Date = None

                class Loan_Relationship:
                    self.Borrower = None
                    self.Lender = None
                    self.Loan_Date = None
                    self.Loan_Amount = None
                ```
                Note that I've identified the following role types:

                1. Plaintiff
                2. Defendant
                3. Lawyer
                4. Court
                5. Judge
                6. Witness
                7. Agent
                8. Borrower
                9. Lender

                And the following relation types:

                1. Representation_Relationship (between Lawyer and Client)
                2. Testimony_Relationship (between Witness and Case)
                3. Authorization_Relationship (between Agent and Principal)
                4. Loan_Relationship (between Borrower and Lender)

                Each role and relation type has its own set of attributes, which are based on the provided information and common sense.
                ''',
                '''
                Here is the constructed Knowledge Graph for the event "民间借贷案件" (Private Lending Case) in the form of a set of Python classes:

                    ```
                    class PrivateLendingCase:
                        self.Case_Number = None
                        self.Case_Type = None
                        self.Court = None
                        self.Filing_Date = None
                        self.Trial_Date = None
                        self.Verdict = None

                    class Plaintiff:
                        self.Name = None
                        self.Address = None
                        self.Lawyer = None
                        self.Agent = None

                    class Defendant:
                        self.Name = None
                        self.Address = None
                        self.Lawyer = None
                        self.Agent = None

                    class Lawyer:
                        self.Name = None
                        self.License_Number = None
                        self.Representing_Party = None

                    class Court:
                        self.Name = None
                        self.Location = None
                        self.Judge = None

                    class Judge:
                        self.Name = None
                        self.Title = None
                        self.Court = None

                    class Witness:
                        self.Name = None
                        self.Testimony = None
                        self.Relation_to_Parties = None

                    class Agent:
                        self.Name = None
                        self.Authorization_Document = None
                        self.Representing_Party = None

                    class Borrower:
                        self.Name = None
                        self.Address = None
                        self.Loan_Amount = None
                        self.Loan_Purpose = None

                    class Lender:
                        self.Name = None
                        self.Address = None
                        self.Loan_Amount = None
                        self.Loan_Terms = None

                    class Loan_Agreement:
                        self.Date = None
                        self.Borrower = None
                        self.Lender = None
                        self.Loan_Amount = None
                        self.Interest_Rate = None

                    class Plaintiff_Defendant_Relationship:
                        self.Plaintiff = None
                        self.Defendant = None
                        self.Relationship_Type = None

                    class Lawyer_Client_Relationship:
                        self.Lawyer = None
                        self.Client = None
                        self.Relationship_Type = None

                    class Court_Case_Relationship:
                        self.Court = None
                        self.Case = None
                        self.Relationship_Type = None

                    class Witness_Testimony_Relationship:
                        self.Witness = None
                        self.Testimony = None
                        self.Relationship_Type = None

                    class Agent_Party_Relationship:
                        self.Agent = None
                        self.Party = None
                        self.Relationship_Type = None

                    class Borrower_Lender_Relationship:
                        self.Borrower = None
                        self.Lender = None
                        self.Relationship_Type = None
                    ```

                    Note that I've identified the following role types and relations based on the provided information:

                    Role Types:

                    * Plaintiff
                    * Defendant
                    * Lawyer
                    * Court
                    * Judge
                    * Witness
                    * Agent
                    * Borrower
                    * Lender

                    Relations:

                    * Plaintiff-Defendant Relationship
                    * Lawyer-Client Relationship
                    * Court-Case Relationship
                    * Witness-Testimony Relationship
                    * Agent-Party Relationship
                    * Borrower-Lender Relationship

                    Each class has attributes that are relevant to the specific role or relation.
                '''
            ]
        }
    }
}
