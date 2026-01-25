import OpenAI from 'openai';

class OpenAIService {
  private openai: OpenAI;

  constructor() {
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });
  }

  async analyzeAssessment(assessmentData: any): Promise<any> {
    try {
      const prompt = `
        You are an AI assistant for an ASD (Autism Spectrum Disorder) floor time intervention system. Analyze the following assessment data and generate a comprehensive child profile.

        Assessment Data:
        ${JSON.stringify(assessmentData, null, 2)}

        Instructions:
        1. Analyze all assessment information
        2. Identify strengths and challenges
        3. Determine developmental levels across key domains
        4. Generate recommendations for intervention
        5. Return the response in JSON format with clear sections

        Response format:
        {
          "profile": {
            "strengths": [],
            "challenges": [],
            "developmentalLevels": {},
            "recommendations": []
          },
          "analysis": "Summary of the assessment analysis"
        }
      `;

      const response = await this.openai.chat.completions.create({
        model: 'gpt-4',
        messages: [
          { role: 'system', content: 'You are an expert in ASD assessment and intervention.' },
          { role: 'user', content: prompt }
        ],
        temperature: 0.3,
        max_tokens: 2000,
      });

      const result = response.choices[0].message?.content;
      if (!result) {
        throw new Error('No response from OpenAI');
      }

      return JSON.parse(result);
    } catch (error) {
      console.error('Error analyzing assessment:', error);
      throw new Error('Failed to analyze assessment');
    }
  }

  async recommendGames(childProfile: any, observations: any): Promise<any> {
    try {
      const prompt = `
        You are an AI assistant for an ASD floor time intervention system. Recommend developmentally appropriate games based on the child profile and session observations.

        Child Profile:
        ${JSON.stringify(childProfile, null, 2)}

        Observations:
        ${JSON.stringify(observations, null, 2)}

        Instructions:
        1. Analyze the child's strengths and challenges
        2. Consider the observation notes
        3. Recommend 3-5 games tailored to the child's needs
        4. Include game name, description, developmental focus, and implementation tips
        5. Return the response in JSON format

        Response format:
        {
          "recommendations": [
            {
              "name": "Game Name",
              "description": "Game description",
              "developmentalFocus": ["domain1", "domain2"],
              "implementationTips": ["tip1", "tip2"]
            }
          ],
          "rationale": "Explanation of why these games were recommended"
        }
      `;

      const response = await this.openai.chat.completions.create({
        model: 'gpt-4',
        messages: [
          { role: 'system', content: 'You are an expert in ASD intervention games and activities.' },
          { role: 'user', content: prompt }
        ],
        temperature: 0.4,
        max_tokens: 2000,
      });

      const result = response.choices[0].message?.content;
      if (!result) {
        throw new Error('No response from OpenAI');
      }

      return JSON.parse(result);
    } catch (error) {
      console.error('Error recommending games:', error);
      throw new Error('Failed to recommend games');
    }
  }

  async analyzeSession(sessionObservations: any): Promise<any> {
    try {
      const prompt = `
        You are an AI assistant for an ASD floor time intervention system. Analyze the session observations and generate a detailed summary.

        Session Observations:
        ${JSON.stringify(sessionObservations, null, 2)}

        Instructions:
        1. Analyze all observation data
        2. Identify key moments and interactions
        3. Note progress and challenges during the session
        4. Highlight areas for improvement
        5. Return the response in JSON format with structured sections

        Response format:
        {
          "summary": {
            "keyMoments": [],
            "progress": [],
            "challenges": [],
            "areasForImprovement": []
          },
          "analysis": "Comprehensive session analysis"
        }
      `;

      const response = await this.openai.chat.completions.create({
        model: 'gpt-4',
        messages: [
          { role: 'system', content: 'You are an expert in analyzing ASD intervention sessions.' },
          { role: 'user', content: prompt }
        ],
        temperature: 0.3,
        max_tokens: 2000,
      });

      const result = response.choices[0].message?.content;
      if (!result) {
        throw new Error('No response from OpenAI');
      }

      return JSON.parse(result);
    } catch (error) {
      console.error('Error analyzing session:', error);
      throw new Error('Failed to analyze session');
    }
  }

  async generateFeedbackForm(sessionSummary: any): Promise<any> {
    try {
      const prompt = `
        You are an AI assistant for an ASD floor time intervention system. Generate a feedback form based on the session summary.

        Session Summary:
        ${JSON.stringify(sessionSummary, null, 2)}

        Instructions:
        1. Create a feedback form with relevant questions
        2. Include sections for parents and educators
        3. Add rating scales and open-ended questions
        4. Focus on key areas from the session
        5. Return the response in JSON format with form structure

        Response format:
        {
          "form": {
            "sections": [
              {
                "title": "Section Title",
                "questions": [
                  {
                    "type": "rating",
                    "question": "Question text",
                    "scale": 1-5,
                    "description": "Optional description"
                  },
                  {
                    "type": "text",
                    "question": "Question text",
                    "description": "Optional description"
                  }
                ]
              }
            ]
          },
          "purpose": "Explanation of the feedback form's purpose"
        }
      `;

      const response = await this.openai.chat.completions.create({
        model: 'gpt-4',
        messages: [
          { role: 'system', content: 'You are an expert in creating feedback forms for ASD interventions.' },
          { role: 'user', content: prompt }
        ],
        temperature: 0.4,
        max_tokens: 2000,
      });

      const result = response.choices[0].message?.content;
      if (!result) {
        throw new Error('No response from OpenAI');
      }

      return JSON.parse(result);
    } catch (error) {
      console.error('Error generating feedback form:', error);
      throw new Error('Failed to generate feedback form');
    }
  }

  async reEvaluateChild(childProfile: any, sessionHistory: any): Promise<any> {
    try {
      const prompt = `
        You are an AI assistant for an ASD floor time intervention system. Re-evaluate the child's progress based on the current profile and session history.

        Current Child Profile:
        ${JSON.stringify(childProfile, null, 2)}

        Session History:
        ${JSON.stringify(sessionHistory, null, 2)}

        Instructions:
        1. Analyze progress across developmental domains
        2. Identify areas of growth and persistent challenges
        3. Update the child profile with new assessment
        4. Generate revised recommendations
        5. Return the response in JSON format with updated profile

        Response format:
        {
          "updatedProfile": {
            "strengths": [],
            "challenges": [],
            "developmentalLevels": {},
            "recommendations": []
          },
          "progressAnalysis": "Detailed analysis of progress",
          "nextSteps": ["step1", "step2"]
        }
      `;

      const response = await this.openai.chat.completions.create({
        model: 'gpt-4',
        messages: [
          { role: 'system', content: 'You are an expert in ASD progress evaluation and assessment.' },
          { role: 'user', content: prompt }
        ],
        temperature: 0.3,
        max_tokens: 2000,
      });

      const result = response.choices[0].message?.content;
      if (!result) {
        throw new Error('No response from OpenAI');
      }

      return JSON.parse(result);
    } catch (error) {
      console.error('Error re-evaluating child:', error);
      throw new Error('Failed to re-evaluate child');
    }
  }
}

export const openAIService = new OpenAIService();
export { OpenAIService };
