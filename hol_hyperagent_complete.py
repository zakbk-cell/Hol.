#!/usr/bin/env python3
"""HOL HyperAgent Phase 1 — Complete Integration"""

import sys
sys.path.insert(0, '/root/Hol.')

from skills_loader import SkillLibrary
import anthropic
import json
import logging
import re
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class HOLHyperAgent:
    """Complete autonomous agent with all skills"""
    
    def __init__(self):
        self.skills = SkillLibrary()
        with open('/root/Hol./.env') as f:
            for line in f:
                if 'ANTHROPIC_API_KEY' in line:
                    api_key = line.split('=')[1].strip()
                    break
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-haiku-4-5"
        logger.info("✅ HOL HyperAgent initialized with 10 skills")
    
    def _parse_json_response(self, response_text):
        """Parse JSON from Claude response, handling markdown wrappers"""
        try:
            # Remove markdown wrappers
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            # Parse JSON
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON object
            match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    return None
            return None
    
    def generate_product_copy(self, product_name, features, target_audience):
        """Generate product copy"""
        logger.info(f"✍️ Generating copy for {product_name}...")
        
        task = f"Write compelling copy for {product_name} (features: {features}) for {target_audience}. Return JSON: {{headline, body, cta}}"
        system_prompt = self.skills.get_system_prompt('copywriting_psychologist', task)
        
        try:
            msg = self.client.messages.create(
                model=self.model, max_tokens=600, system=system_prompt,
                messages=[{"role": "user", "content": "Generate copy as JSON only."}]
            )
            copy_data = self._parse_json_response(msg.content[0].text)
            return {"type": "copy", "data": copy_data, "status": "Generated"}
        except Exception as e:
            logger.error(f"❌ {e}")
            return {"status": "failed", "error": str(e)}
    
    def optimize_pricing(self, product_name, product_cost, market_avg, target_audience):
        """Generate 3-tier pricing"""
        logger.info(f"💰 Optimizing pricing for {product_name}...")
        
        task = f"Create 3-tier pricing for {product_name} (cost: ${product_cost}, market: ${market_avg}). Return JSON: {{tier_1: {{price, features}}, tier_2: {{price, features}}, tier_3: {{price, features}}}}"
        system_prompt = self.skills.get_system_prompt('price_psychology_strategist', task)
        
        try:
            msg = self.client.messages.create(
                model=self.model, max_tokens=800, system=system_prompt,
                messages=[{"role": "user", "content": "Generate 3-tier pricing as JSON."}]
            )
            pricing = self._parse_json_response(msg.content[0].text)
            return {"type": "pricing", "data": pricing, "status": "Generated"}
        except Exception as e:
            logger.error(f"❌ {e}")
            return {"status": "failed"}
    
    def generate_email_sequence(self, product_name, product_price, target_audience, benefit, problem):
        """Generate 6-email sequence"""
        logger.info(f"📧 Generating 6-email sequence for {product_name}...")
        
        task = f"Create 6-email sequence for {product_name} at {product_price} to {target_audience}. Return JSON: {{email_1: {{subject, body, cta, day}}, ..., email_6: {{...}}}}"
        system_prompt = self.skills.get_system_prompt('sequence_psychologist', task)
        
        try:
            msg = self.client.messages.create(
                model=self.model, max_tokens=1500, system=system_prompt,
                messages=[{"role": "user", "content": "Generate 6 emails as JSON."}]
            )
            emails = self._parse_json_response(msg.content[0].text)
            return {"type": "emails", "data": emails, "status": "Generated"}
        except Exception as e:
            logger.error(f"❌ {e}")
            return {"status": "failed"}
    
    def generate_full_campaign(self, product_name, product_price, product_cost, market_avg, features, target_audience, benefit, problem):
        """Generate complete campaign"""
        logger.info("\n" + "="*70)
        logger.info(f"🚀 GENERATING FULL CAMPAIGN: {product_name}")
        logger.info("="*70)
        
        campaign = {
            "product": product_name,
            "created_at": datetime.now().isoformat(),
            "components": {}
        }
        
        # Generate all components
        campaign["components"]["copy"] = self.generate_product_copy(product_name, features, target_audience)
        campaign["components"]["pricing"] = self.optimize_pricing(product_name, product_cost, market_avg, target_audience)
        campaign["components"]["emails"] = self.generate_email_sequence(product_name, product_price, target_audience, benefit, problem)
        
        logger.info("\n" + "="*70)
        logger.info("✅ CAMPAIGN COMPLETE")
        logger.info("="*70)
        
        return campaign
    
    def save_campaign(self, campaign):
        """Save campaign"""
        import os
        os.makedirs('/root/Hol./campaigns', exist_ok=True)
        filename = f"/root/Hol./campaigns/{campaign['product']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(campaign, f, indent=2)
        logger.info(f"💾 Saved: {filename}")
        return filename

if __name__ == "__main__":
    agent = HOLHyperAgent()
    
    campaign = agent.generate_full_campaign(
        product_name="Fashion AI Stylist",
        product_price="$79/month",
        product_cost=10,
        market_avg=79,
        features="AI photo generation, background removal",
        target_audience="E-commerce founders",
        benefit="Generate photos 10x faster",
        problem="Manual photography takes 50+ hours/month"
    )
    
    filename = agent.save_campaign(campaign)
    
    print("\n" + "="*70)
    print("CAMPAIGN COMPONENTS:")
    for comp, data in campaign['components'].items():
        status = data.get('status', 'Unknown')
        print(f"  ✅ {comp}: {status}")
    print(f"\n📁 Saved to: {filename}")
    print("="*70)
